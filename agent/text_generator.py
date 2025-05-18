"""
Text generators as Interfaces/Abstract Base Class
"""
import logging
import random
from abc import ABC, abstractmethod

import google.generativeai as genai
from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer

from agent.utils import get_post_prompt, sentiment_analysis
from project.const import Stage, TEMPLATES, Result
from project.setings import get_key


LOGGER = logging.getLogger(__name__)

# TODO: Maybe a Protocol to keep up with the times
class TextGenerator(ABC):
    @abstractmethod
    def generate_post(self, context: dict) -> str:
        pass

    @abstractmethod
    def generate_reply(self, context: dict, original_comment: str) -> str:
        pass
    
    @abstractmethod
    def generate_mention_post(self, context: dict, entity_to_mention: str, base_message: str) -> str:
        pass


class TemplateBasedTextGenerator(TextGenerator):
    """
    Generates text using predefined templates and racer vocabulary. Uses a sentiment analysis for replies
    """
    def __init__(self):
        self.templates = TEMPLATES

    def _get_race_name_placeholder(self, context: dict):
        return context.get("race_name", "SilverstoneGP")

    def _get_stage_abbr(self, stage: Stage):
        return stage.short_name

    def generate_post(self, context: dict) -> str:
        stage = context.get("stage", Stage.FP1)
        result: Result | None = context.get("result")
        team_name = context.get("team_name", "Mach 5")
        race_name = self._get_race_name_placeholder(context)
        stage_abbr = self._get_stage_abbr(stage)

        # Set up default context before calculating it
        key = "practice_1"
        result_detail_for_quali = str(result) if result else "a good spot"
        suffix = ""

        # Use result and stage to set up the right template
        if result:
            if result == Result.P1:
                suffix = "_win"
            elif result in [Result.P2, Result.P3, Result.P4, Result.P5, Result.TOP_3, Result.TOP_5]:
                suffix = "_good_result"
            elif result == Result.DNF:
                suffix = "_dnf"
            elif result in [getattr(Result, f"P{i}") for i in range(6, 21)]:
                suffix = "_difficult_race"
            else:
                suffix = "_difficult_race"

        # If it was a race then we do not need extra placing context, just result
        if stage == Stage.RACE and suffix:
            key = suffix[1:] # Remove underscore
        # If it was qualifying then we need extra placing context
        elif stage in [Stage.Q1, Stage.Q2, Stage.Q3]:
            if stage == Stage.Q1:
                key = f"qualifying_1{suffix}"
            elif stage == Stage.Q2: #
                key = f"qualifying_2{suffix}"
            else:
                key = f"qualifying_3{suffix}"
            if result:
                result_detail_for_quali = result
        # If it was practice then we need extra placing context
        elif stage in [Stage.FP1, Stage.FP2, Stage.FP3]:
            if stage == Stage.FP1:
                key = f"practice_1{suffix}"
            elif stage == Stage.FP2:
                key = f"practice_2{suffix}"
            else:
                key = f"practice_3{suffix}"
        # Not necessary but elif's look better with an else clause
        else:
            key = "practice_1"
        LOGGER.debug(f"Calling template - {key}")
        template_list = self.templates.get(key, self.templates["practice_1"])
        chosen_template = random.choice(template_list)
        
        # Inject context using string formating
        return chosen_template.format(
            team_name=team_name,
            race_name=race_name,
            stage=stage.value,
            stage_abbr=stage_abbr,
            result_detail=result_detail_for_quali
        )

    def generate_reply(self, context: dict, original_comment: str) -> str:
        racer_name = context.get("racer_name", "I")
        compound_score = sentiment_analysis(original_comment)

        LOGGER.debug(f"Fan comment: '{original_comment}', Sentiment (compound): {compound_score}")

        if compound_score >= 0.05:
            reply_list = self.templates["reply_positive"]
        elif compound_score <= -0.05:
            reply_list = self.templates["reply_negative"]
        elif compound_score is None:
            # Fallback if NLTK/VADER is not available
            reply_list = self.templates["reply_neutral"]
        else:
            reply_list = self.templates["reply_neutral"]
    

        return f"{racer_name} replies: {random.choice(reply_list)}"

    def generate_mention_post(self, context: dict, entity_to_mention: str, base_message: str) -> str:
        compound_score = sentiment_analysis(base_message)
        if compound_score >= 0.05:
            message = f"{base_message}, Big shoutout to @{entity_to_mention}!"
        elif compound_score <= -0.05:
            message = f"{base_message} But still a huge shoutout to @{entity_to_mention}!"
        else:
            # Fallback if NLTK/VADER is not available or neutral
            message = f"{base_message} Shoutout to @{entity_to_mention}!"
        
        if context["stage"] == Stage.RACE and context["result"] == Result.P1:
            message += f" #Team{context['team_name']} #Winner"

        return message


class GeminiTextGenerator(TextGenerator):
    def __init__(self):
        api_key = get_key()
        if not api_key:
            LOGGER.error("GOOGLE_API_KEY not found in environment variables." \
            " Please set it in your .env file.")
            raise ValueError("GOOGLE_API_KEY not found. Cannot initialize GeminiTextGenerator.")
        
        try:
            genai.configure(api_key=api_key)
            # Gemini-1.5-flash is still fast and cheaper than the 
            # Newer 2.0 models whilst being a capable LLM
            self.model = genai.GenerativeModel('gemini-1.5-flash-latest')
            LOGGER.info(f"GeminiTextGenerator initialized with model: {self.model.model_name}")
        except Exception as e:
            LOGGER.error(f"Failed to configure Gemini or initialize model: {e}", exc_info=True)
            raise

    def _generate_text_with_gemini(self, prompt_text: str) -> str:
        try:
            LOGGER.debug(f"Prompt: {prompt_text}")
            # TODO: Configure generation parameters, but not necessary in this demo
            # Adding a token limit tends to truncate Gemini's though proccess :) 
            generation_config = genai.types.GenerationConfig(
                temperature=0.5
            )
            response = self.model.generate_content(
                prompt_text,
                generation_config=generation_config
            )

            if not response.candidates:
                block_reason_message = "Unknown reason"
                # If content is blocked, return reason
                if response.prompt_feedback and response.prompt_feedback.block_reason:
                    block_reason_message = response.prompt_feedback.block_reason_message or \
                        response.prompt_feedback.block_reason.name
                LOGGER.warning(
                    f"Content generation blocked by Gemini API. Reason: {block_reason_message}"
                    )
                return f"[Content blocked by API: {block_reason_message}]"
            # If there is generated content, return it
            if response.candidates[0].content and response.candidates[0].content.parts:
                generated_text = "".join(part.text for part in response.candidates[0].content.parts)
                return generated_text.strip()
            else:
                LOGGER.warning("Gemini API returned a candidate with no content parts.")
                return "Sorry, I received an unexpected response format from the AI."

        except Exception as e:
            LOGGER.error(f"Error calling Gemini API: {e}", exc_info=True)
            return "An error occurred while trying to generate text with Gemini."

    def _create_gemini_prompt(self, context: dict, task_instruction: str) -> str:
        racer_name = context.get('racer_name', 'Go Mifune')
        team_name = context.get('team_name', 'Mach 5')
        
        prompt_parts = [
            f"You are {racer_name}, a charismatic and highly skilled Formula 1 racer for the"
            f" {team_name} team.",
            "Your social media persona is engaging, passionate, and authentic. You often "
            "share insights, express emotions clearly, and interact positively with fans.",
            f"Current Race Event: {context.get('race_name', 'SilverstoneGP')} 2025.",
        ]

        current_stage: Stage = context.get('stage')
        prompt_parts.append(
            f"Current Stage: {current_stage.value if current_stage else 'practice 1'}."
        )
        current_result: Result | None = context.get('result')
        if current_result:
            prompt_parts.append(f"Most Recent Result: {str(current_result)}.")
        
        prompt_parts.append(f"\nYour Task: {task_instruction}")
        return "\n".join(prompt_parts)

    def generate_post(self, context: dict) -> str:
        # Fine tuned prompts for different scenarios
        current_stage: Stage = context.get('stage')
        if current_stage == Stage.RACE and context.get('result') == Result.P1:
            instruction = f"Craft an ecstatic and thankful social media post celebrating your" \
                f" P1 victory. Highlight the team's effort ({context.get('team_name', 'Mach 5')})"\
                " and the thrill of the win. Use F1-style hashtags."
            
        elif current_stage == Stage.RACE and context.get('result') == Result.DNF:
            instruction = "Compose a social media post reflecting disappointment about a DNF, "
            "but also showing resilience and determination to bounce back. Include hashtags "
            "like #NeverGiveUp."
        elif current_stage in [Stage.FP1, Stage.FP2, Stage.FP3]:
            instruction = f"Write a focused social media post about the current"
            f"{current_stage.value if current_stage else 'practice'} session, mentioning car "
            "feel or data gathering. Include relevant hashtags."
        else:
            instruction = "Create a general social media update suitable for an F1 racer, reflecting"
            " the current context. Include appropriate hashtags."
        
        prompt = self._create_gemini_prompt(context, instruction)
        LOGGER.debug(f"Gemini Post Prompt:\n{prompt}")
        return self._generate_text_with_gemini(prompt)

    def generate_reply(self, context: dict, original_comment: str) -> str:
        instruction = f"A fan, @trixie, commented: {original_comment}. Write a short, appreciative,"
        "and cool reply. Keep it brief, friendly, and authentic. Acknowledge their sentiment "
        "if appropriate. Do not dwell into negativity. Always use F1 enthusiasm and character."
        prompt = self._create_gemini_prompt(context, instruction)
        LOGGER.debug(f"Gemini Reply Prompt:\n{prompt}")
        return self._generate_text_with_gemini(prompt)

    def generate_mention_post(
            self, context: dict, entity_to_mention: str, base_message: str
        ) -> str:
        instruction = f"Create a social media post that incorporates this idea: '{base_message}'. "
        f"Make sure to prominently feature and praise '{entity_to_mention}' using an"
        f"@{entity_to_mention} like on Twitter. Use relevant F1-style hashtags. You can give "
        "them a shout out"
        prompt = self._create_gemini_prompt(context, instruction)
        LOGGER.debug(f"Gemini Mention Prompt:\n{prompt}")
        return self._generate_text_with_gemini(prompt)


class TransformerTextGenerator(TextGenerator):
    # TODO: Find a better light weight model, distilgpt2 sucks, 
    # But also the resources presented to it are minimal in this demo
    def __init__(self, model_name: str = "distilgpt2"):
        self.generator = pipeline("text-generation", model=model_name)


    def _create_prompt_for_post(self, context: dict) -> str:
        # TODO: Prompts could be shorter and concise since the model is not that powerful
        # And resource-starved
        prompt = f"You are {context.get('racer_name', 'Go Mifune')} an F1 racer from the imaginary team {context.get('team_name', 'Mach 5')}. "
        prompt += "You are very passionate about racing and social media; and engage a lot with fans and strangers alike. "
        prompt += f"The current race is {context.get('race_name', 'the Grand Prix')} 2025. "

        current_stage: Stage = context.get('stage')
        prompt += f"The current stage is {current_stage.value if current_stage else 'practice'}. "
        current_result: Result | None = context.get('result')
        if current_result:
            prompt += f"Your last race result was {str(current_result)}. "
        return get_post_prompt(prompt, context, context.get('stage'), context.get('result'))

    def generate_post(self, context: dict) -> str:
        prompt = self._create_prompt_for_post(context)
        LOGGER.debug(f"Prompt: {prompt}")
        # These configs are arbirtary just to tweak a few things and squeeze some
        # Better performance with the model, the model is not good!
        generated_sequences = self.generator(
            prompt,
            max_new_tokens=200,
            num_return_sequences=1,
            pad_token_id=self.generator.tokenizer.eos_token_id,
            do_sample=True,
            temperature=0.75,
            top_k=50,
            top_p=0.92,
            no_repeat_ngram_size=2,
            truncation=True
        )
        post_text = generated_sequences[0]['generated_text']
        
        # Clean up the prompt from the generated text if the model includes it
        if post_text.startswith(prompt):
             post_text = post_text[len(prompt):].strip()
        return post_text


    def _create_prompt_for_reply(self, context: dict, original_comment: str) -> str:
        prompt = f"You are {context.get('racer_name', 'Go')}, an F1 racer. You are very passionate about social media, and engage a lot with fans and strangers alike. A fan named @trixie commented: '{original_comment}'. "
        prompt += "Write a short, appreciative, and cool reply to this fan even if they are being negative to you. Keep it brief. You can check sentiment and re-iterate some of their thoughts."
        return prompt

    def generate_reply(self, context: dict, original_comment: str) -> str:
        prompt = self._create_prompt_for_reply(context, original_comment)
        LOGGER.debug(f"Prompt: {prompt}")
        generated_sequences = self.generator(
            prompt,
            max_new_tokens=150,
            num_return_sequences=1,
            pad_token_id=self.generator.tokenizer.eos_token_id,
            do_sample=True,
            temperature=0.7,
            top_k=50,
            top_p=0.9,
            no_repeat_ngram_size=2,
            truncation=True)
        reply_text = generated_sequences[0]['generated_text']

        if reply_text.startswith(prompt):
            reply_text = reply_text[len(prompt):].strip()
        return reply_text
    
    def generate_mention_post(self, context: dict, entity_to_mention: str, base_message: str) -> str:
        instruction = f"Create a social media post that incorporates this idea: '{base_message}'. Make sure to prominently feature and praise '{entity_to_mention}' using an"
        f"@{entity_to_mention} like on Twitter. Use relevant F1-style hashtags. You can give "
        "them a shout out"
        
        prompt = f"You are {context.get('racer_name', 'Go Mifune')} an F1 racer from the imaginary team {context.get('team_name', 'Mach 5')}. "
        prompt += "You are very passionate about racing and social media. "
        prompt += f"The current race is {context.get('race_name', 'the Grand Prix')} 2025. "
        prompt += f"Current Stage: {context.get('stage').value if context.get('stage') else 'an unknown session'}. {instruction}"
        
        generated_sequences = self.generator(
            prompt,
            max_new_tokens=150,
            num_return_sequences=1,
            pad_token_id=self.generator.tokenizer.eos_token_id,
            do_sample=True, temperature=0.75, top_k=50, top_p=0.92, no_repeat_ngram_size=2,
            truncation=True
        )
        post_text = generated_sequences[0]['generated_text']
        if post_text.startswith(prompt):
             post_text = post_text[len(prompt):].strip()
        return post_text
