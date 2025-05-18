"""
Store all project constants here. NLTK would be perfect for entity extraction for Stage and Race Enums
but it is overkill and simple regex based string manipulation is used instead.
"""
from enum import Enum
import re
from typing import Optional

class Stage(Enum):
    FP1 = "Free Practice 1"
    FP2 = "Free Practice 2"
    FP3 = "Free Practice 3"
    Q1 = "Qualifying 1"
    Q2 = "Qualifying 2"
    Q3 = "Qualifying 3"
    RACE = "The Grand Prix (Race)"

    # Return a readable version for object deconstruction
    def __str__(self):
        return self.value

    @property
    def short_name(self):
        if "Practice" in self.value:
            return f"FP{self.name[-1]}"
        elif "Qualifying" in self.value:
            return f"Q{self.name[-1]}"
        elif self == Stage.RACE:
            return "Race"
        return self.name


# As a first approach, try to full match some F1 stages
# TODO: Maybe add sprint stages for a full solution
_stage_mapping = {
    r"fp1": Stage.FP1,
    r"free practice 1": Stage.FP1,
    r"practice 1": Stage.FP1,
    r"fp2": Stage.FP2,
    r"free practice 2": Stage.FP2,
    r"practice 2": Stage.FP2,
    r"fp3": Stage.FP3,
    r"free practice 3": Stage.FP3,
    r"practice 3": Stage.FP3,
    r"fp": Stage.FP3,  # In the case of just unqualified practice assume the last
    r"practice": Stage.FP3,
    r"free practice": Stage.FP3,

    r"q1": Stage.Q1,
    r"qualifying 1": Stage.Q1,
    r"q2": Stage.Q2,
    r"qualifying 2": Stage.Q2,
    r"q3": Stage.Q3,
    r"qualifying 3": Stage.Q3,
    r"q": Stage.Q3, # In the case of just unqualified qualifying stage assume the last
    r"qualifying": Stage.Q3,
    r"quali": Stage.Q3,

    r"race": Stage.RACE,
    r"grand prix": Stage.RACE,
    r"gp": Stage.RACE,
}


# TODO: NLTK would do this in less lines and handle fuzz logic
def parse_stage_input(user_input: str) -> Stage | None:
    """
    Parses user input string and maps it to a Stage Enum.
    Applies default rules for "practice" (FP3) and "qualifying" (Q3).
    Returns None if no valid stage is found.
    """
    normalized_input = user_input.lower().strip()

    # Check for exact matches first using the mapping keys as patterns
    for pattern, stage_enum in _stage_mapping.items():
        if re.fullmatch(pattern, normalized_input):
            return stage_enum
    
    # Try and match numbered stages for practice
    match_fp = re.fullmatch(r"(?:fp|free practice|practice)\s*([1-3])", normalized_input)
    if match_fp:
        num = match_fp.group(1)
        return getattr(Stage, f"FP{num}", None)

    # Try and match numbered stages for qualifying
    match_q = re.fullmatch(r"(?:q|qualifying|quali)\s*([1-3])", normalized_input)
    if match_q:
        num = match_q.group(1)
        return getattr(Stage, f"Q{num}", None)

    return None


class Result(Enum):
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"
    P4 = "P4"
    P5 = "P5"
    P6 = "P6"
    P7 = "P7"
    P8 = "P8"
    P9 = "P9"
    P10 = "P10"
    P11 = "P11"
    P12 = "P12"
    P13 = "P13"
    P14 = "P14"
    P15 = "P15"
    P16 = "P16"
    P17 = "P17"
    P18 = "P18"
    P19 = "P19"
    P20 = "P20"
    DNF = "DNF"
    TOP_3 = "Top 3"
    TOP_5 = "Top 5"

    # Return a readable version for object deconstruction
    def __str__(self):
        return self.value

    # Use a class method to parse string into a result enum
    # TODO: Use NLTK or another package for more nuanced extraction
    @classmethod
    def from_string(cls, input_str: str) -> Optional['Result']:
        if not input_str:
            return None

        s_clean = input_str.strip().lower()

        # 1. DNF check
        if "dnf" in s_clean or "did not finish" in s_clean:
            return cls.DNF

        # 2. Exact P* match e.g p1 so long as there's a digit
        m = re.fullmatch(r"p(\d+)", s_clean)
        if m:
            num = int(m.group(1))
            if 1 <= num <= 20:
                return getattr(cls, f"P{num}", None)

        # 3. F1 jargon for a win, this is where extraction and sentiment can shine
        if "win" in s_clean or "pole" in s_clean:
            return cls.P1

        # 4. Top 3 case, still check digits if entered
        if "podium" in s_clean:
            px_search = re.search(r"\bp(\d+)\b", s_clean)
            if px_search:
                num = int(px_search.group(1))
                if 1 <= num <= 3: return getattr(cls, f"P{num}", cls.TOP_3)
            return cls.TOP_3

        # 5. Top 5 case, still check digits if entered
        if "good" in s_clean:
            px_search = re.search(r"\bp(\d+)\b", s_clean)
            if px_search:
                num = int(px_search.group(1))
                if 1 <= num <= 5: return getattr(cls, f"P{num}", cls.TOP_5)
            return cls.TOP_5

        return None


# Templates for the agent's basic text responses. A lot of samples have been added to create a 
# Level of character to the agent even though it is really a static but randomized set
# Sprint responses added but not used in this basic solution
TEMPLATES = {
    "win": [
        "YES! CHECKERED FLAG! 🏆 What a race! The Mach 5 was absolutely flying today! Huge thanks to the entire #Team{team_name} for their incredible work. We pushed the limits and it paid off! Feeling on top of the world! #Winner #F1 #{race_name}GP #GoMachGo 🚀",
        "P1, BABY! 🥇 That was for all the fans! The roar of the crowd, the speed of the Mach 5... unbelievable! Massive shoutout to the crew, faultless strategy! We are #Team{team_name}! #F1Victory #{race_name} #ChampionSpirit ✨",
        "VICTORY!!! 🍾 Splashed that champagne with pride! This one means a lot. Every single member of #Team{team_name} poured their heart into this. The Mach 5 was a dream to drive today! #F1 #{race_name}GP #Podium #Mach5Speed 💨",
        "WE DID IT! Crossed the line in FIRST! 🤩 The strategy was bold, the pit stops were perfect, and the Mach 5 felt like an extension of me. Thank you #Team{team_name} and all the amazing fans! #F1Winner #{race_name} #RacingGlory 🎌",
        "That's the top step! 🥳 What an incredible feeling to bring home the win for #Team{team_name} at #{race_name}! The Mach 5 handled like a beauty. This is what we work for! #F1 #{race_name}GP #SpeedDemon #VictoryLap 🌟"
    ],
    "good_result": [
        "Solid points in the bag! 💪 The Mach 5 showed great pace today at #{race_name}. Happy with the performance, and we're hungry for more! Thanks for the amazing support, #Team{team_name} fans! #F1 #PointsFinish #KeepPushing 🏎️💨",
        "Good haul of points for #Team{team_name}! The battle out there was intense, but the Mach 5 was a trusty steed. We're definitely making strides! Onwards and upwards to the next one! #{race_name}GP #F1Racing #Progress 📈",
        "Strong result today! Proud of the effort from everyone at #Team{team_name}. The Mach 5 felt really balanced. Every point counts in this championship! Thanks for cheering us on! #F1 #{race_name} #PodiumPush 🚀",
        "Really happy with that performance! Brought home some crucial points for #Team{team_name}. The track was challenging, but the Mach 5 was up to it! Big thanks to the fans! #{race_name} #F1Driver #Determined 💯",
        "A good day at the office with a solid points finish! The Mach 5 felt fantastic and the team did an amazing job. We'll take this momentum forward! #F1 #{race_name}GP #Team{team_name} #RacingSpirit 🔥"
    ],
    "difficult_race": [
        "Not the Sunday we hoped for here at #{race_name}. Gave it absolutely everything out there, but luck wasn't on our side with the Mach 5 today. We'll dig deep, analyze, and come back fighting! Thanks for sticking with us, #Team{team_name}! #NeverGiveUp #F1 🙏",
        "Tough race today. Pushed the Mach 5 to its limits, but it just wasn't our day. Disappointed, but these moments make us stronger. Massive thanks to the #Team{team_name} crew for their non-stop effort. We'll be back! #F1Racing #LearnAndImprove 👊",
        "A challenging Grand Prix, that's for sure. We faced some hurdles and the Mach 5 didn't have the pace we needed. But we don't back down! We'll learn from this and push harder. Appreciate the support! #{race_name} #Team{team_name} #F1Journey 💪",
        "Definitely a character-building day. Things just didn't click for us and the Mach 5. But the spirit of #Team{team_name} is strong! We'll analyze everything and aim to bounce back with speed! #{race_name}GP #F1 #KeepFighting 🎌",
        "Well, that was a tricky one. The Mach 5 felt a bit off balance and we couldn't make the progress we wanted. But that's racing sometimes! We'll put our heads down and work for a better result next time. Thanks for the cheers! #F1 #{race_name} #Team{team_name} ❤️"
    ],
    "dnf": [
        "Absolutely gutted. A DNF is always a tough one to take, especially when the Mach 5 felt promising. Something let go. Huge apologies to the entire #Team{team_name}. We'll investigate thoroughly and come back with a vengeance. #F1 #{race_name} #Heartbreak 💔",
        "That's a premature end to our #{race_name} GP. So frustrating for me and #Team{team_name}. Was pushing hard in the Mach 5 and then... race over. We'll find out what happened and be back stronger. #Resilience #F1Driver 🛠️",
        "DNF. Not the words any driver wants to say. Gutted for #Team{team_name} after all the hard work. The Mach 5 deserved better today. We win together, we lose together. We'll bounce back. #F1 #{race_name} #Unlucky 😔",
        "Unfortunately, our race ended early. It's a bitter pill for #Team{team_name} and me. The Mach 5 had more to give. We'll analyze the issue and make sure we're ready for the next battle. #F1 #{race_name}GP #NeverSurrender ⚔️",
        "Race cut short by a technical issue on the Mach 5. So disappointed for #Team{team_name} and all our amazing fans. We'll dig into it and ensure we're fighting fit next time out! #F1 #{race_name} #OnwardsAndUpwards 🚀"
    ],
    "practice_1": [
        "Getting some good laps in during {stage}. Feeling comfortable with the car. Let's keep pushing! #{race_name} #{stage_abbr}",
        "Productive session on track. Lots of data gathered. Car balance is feeling promising. #F1 #{stage_abbr}"
    ],
    "practice_1_win": [
        "P1 in {stage_abbr}! 🚀 The Mach 5 feels like a rocket right out of the box here at #{race_name}! Fantastic start for #Team{team_name}. Lots of data, and a great baseline. Let's keep this fire burning! #F1 #FastestLap #GoMachGo",
        "Topping the timesheets in {stage}! What a way to kick off the weekend with #Team{team_name}. The Mach 5 is hooked up! More to come, but this feels GOOD! #F1 #{race_name} #{stage_abbr} #Mach5onTop ✨",
        "That's P1 in {stage} for the Mach 5! Brilliant work by the #Team{team_name} crew. Car feels balanced, and the track is awesome. Positive vibes all around! #{race_name} #{stage_abbr} #LeadingThePack 💨"
    ],
    "practice_1_good_result": [
        "Solid first run in {stage_abbr}! The Mach 5 is showing good potential here at #{race_name}. Happy with that initial pace for #Team{team_name}. Building a strong foundation! #F1 #Practice #MakingProgress 💪",
        "Good vibes after {stage}! The Mach 5 is in a decent window. Lots learned, and we know where to find more time. #Team{team_name} is on it! #{race_name} #{stage_abbr} #F1isGO 🏎️",
        "Positive start in {stage_abbr}! The Mach 5 feels good, and we're in the mix. Plenty of data for #Team{team_name} to analyze. Onwards and upwards! #{race_name} #F1 #KeepPushing 💯"
    ],
    "practice_1_difficult_race": [
        "Tricky first session in {stage_abbr}. The Mach 5 isn't quite where we want it yet here at #{race_name}. Lots of work ahead for #Team{team_name}, but we love a challenge! We'll dig into the data. #F1 #Practice #HardWorkPaysOff 🛠️",
        "Not the smoothest {stage} for us. Still searching for the sweet spot with the Mach 5. But #Team{team_name} is already on the case! Plenty of time to turn it around. #{race_name} #{stage_abbr} #NeverGiveUp 🙏",
        "A challenging start in {stage_abbr}. We've got some homework to do with the Mach 5's balance. But that's what practice is for! #Team{team_name} will get it sorted. #{race_name} #F1 #LearningCurve 🧐"
    ],
    "practice_1_dnf": [
        "Tricky first session in {stage_abbr}. The Mach 5 isn't quite where we want it yet here at #{race_name}. Lots of work ahead for #Team{team_name}, but we love a challenge! We'll dig into the data. #F1 #Practice #HardWorkPaysOff 🛠️",
        "Not the smoothest {stage} for us. Had to abort mission, still searching for the sweet spot with the Mach 5. But #Team{team_name} is already on the case! Plenty of time to turn it around. #{race_name} #{stage_abbr} #NeverGiveUp 🙏",
        "A challenging start in {stage_abbr}. We've got some homework to do with the Mach 5's balance. But that's what practice is for! #Team{team_name} will get it sorted. #{race_name} #F1 #LearningCurve 🧐"
    ],
    "practice_2": [
        "Definitely getting the better of that last chicane. Car's great and the watehr radar is promising. Let's go! #{race_name} #{stage_abbr}",
        "By a tenth of a second! Tires maybe #{stage_abbr}"
    ],
    "practice_2_win": [
        "P1 again in {stage_abbr}! 🔥 The Mach 5 is absolutely on fire today at #{race_name}! #Team{team_name} is delivering a beast! Race pace sims felt strong too. What a Friday! #F1 #Fastest #DominatingPractice 🏆",
        "Top of the charts for {stage}! The Mach 5 is pure joy to drive around here. Huge props to #Team{team_name} for the continuous improvements. Feeling confident! #{race_name} #{stage_abbr} #Mach5Unleashed ⚡",
        "Another P1 in {stage_abbr}! The Mach 5 is loving this track. Great consistency and speed. #Team{team_name} is doing an incredible job. Ready for tomorrow! #{race_name} #F1 #PracticeHero 🎌"
    ],
    "practice_2_good_result": [
        "Strong {stage_abbr} session! The Mach 5 is really coming together. Good long run pace and tyre understanding for #Team{team_name}. Positive signs for qualifying! #{race_name} #F1 #LookingGood 👍",
        "Happy with our work in {stage}! The Mach 5 is competitive, and we've made good setup progress. #Team{team_name} is working seamlessly. #{race_name} #{stage_abbr} #F1Ready 💪",
        "Productive {stage_abbr}! Found some good improvements with the Mach 5. Consistently in the top group. #Team{team_name} and I are feeling optimistic! #{race_name} #F1 #PushingLimits 💥"
    ],
    "practice_2_difficult_race": [
        "A bit of a mixed bag in {stage_abbr}. The Mach 5 showed flashes of speed, but still chasing consistency here at #{race_name}. #Team{team_name} will be burning the midnight oil! We'll get there. #F1 #Practice #DataDive 📊",
        "Struggled a bit for balance in {stage}. The Mach 5 isn't quite singing yet. But we've got a clear direction thanks to the hard work of #Team{team_name}. More to unlock! #{race_name} #{stage_abbr} #F1Challenge ⚙️",
        "Not the easiest {stage_abbr}. Had to wrestle the Mach 5 a bit. But these challenges make us stronger! #Team{team_name} has plenty of ideas for FP3. #{race_name} #F1 #KeepFightingSpirit 🥊"
    ],
    "practice_2_dnf": [
        "A bit of a mixed bag in {stage_abbr}. The Mach 5 showed flashes of speed for the first sector but then we just stalled! #{race_name}. #Team{team_name} will be burning the midnight oil! We'll get there. #F1 #Practice #DataDive 📊",
        "Not a good look! #{race_name} #{stage_abbr} #F1Challenge ⚙️",
        "Oh well! #{race_name} #{stage_abbr} #F1Challenge ⚙️"
    ],
    "practice_3": [
        "Last one for today - {stage}. Felt like I was on skates on that last corner, but we push! #{race_name} #{stage_abbr}",
        "It is still the beginning! #F1 #{stage_abbr}"
    ],
    "practice_3_win": [
        "P1 in final practice ({stage_abbr})! 🚀 The Mach 5 is absolutely dialed in for qualifying at #{race_name}! Perfect way to end practice for #Team{team_name}. Feeling unstoppable! Let's GOOO! #F1 #QualiPrep #PolePositionHungry 🥇",
        "Topped {stage}! The Mach 5 feels incredible. #Team{team_name} has given me a monster for qualifying. Maximum attack incoming! #{race_name} #{stage_abbr} #Mach5ReadyToStrike 🐍",
        "That's P1 in {stage_abbr}! What a confidence booster before qualifying. The Mach 5 is a dream. Thanks, #Team{team_name}! Now for the main event of Saturday! #{race_name} #F1 #FinalPracticeWin 🎯"
    ],
    "practice_3_good_result": [
        "Solid final practice in {stage_abbr}! The Mach 5 is right where we want it for qualifying. Good feeling, good pace. #Team{team_name} has done a stellar job. Bring on quali! #{race_name} #F1 #ReadyToQualify ✨",
        "Happy with {stage}! The Mach 5 is showing strong qualifying potential. We've got a good package thanks to #Team{team_name}. Time to unleash it! #{race_name} #{stage_abbr} #F1QualiMode  aktiviert! (German for activated!)  ενεργοποιήθηκε! (Greek for activated!)  активирован! (Russian for activated!)  aktiviert! (German for activated!)",
        "Good run in {stage_abbr} to wrap up practice. The Mach 5 feels sharp and responsive. #Team{team_name} and I are ready to give it everything in qualifying! #{race_name} #F1 #AllSetForQuali 🔥"
    ],
    "practice_3_difficult_race": [
        "A challenging {stage_abbr} before qualifying. Still some fine-tuning needed on the Mach 5 here at #{race_name}. #Team{team_name} is working flat out. We'll give it our best shot! #F1 #QualiChallenge #Believe 🤞",
        "Not the ideal final practice. The Mach 5 felt a bit unpredictable. But #Team{team_name} are magicians! We'll analyze quickly and fight hard in qualifying. #{race_name} #{stage_abbr} #F1Push 🛠️",
        "Struggled to find the perfect balance in {stage}. The Mach 5 has more potential, we just need to unlock it for qualifying. #Team{team_name} knows what to do! #{race_name} #F1 #FocusOnQuali 集中! (Japanese for Focus!)"
    ],
    "practice_3_dnf": [
        "A challenging {stage_abbr} before qualifying. Still some fine-tuning needed on the Mach 5 #F1 #QualiChallenge #Believe 🤞",
        "Politics!. But #Team{team_name} are magicians! We'll analyze quickly and fight hard in qualifying. #{race_name} #{stage_abbr} #F1Push 🛠️",
        "Struggled to find the perfect balance in {stage}. The Mach 5 has more potential, we just need to unlock it for qualifying. #Team{team_name} knows what to do! #{race_name} #F1 #FocusOnQuali 集中! (Japanese for Focus!)"
    ],
    "qualifying_1": [
        "Made it past the first qualification with {result_detail}. We'll give it everything next round! #F1 #{race_name} #Qualifying",
        "That last right-hander was intense! {result_detail} for now. Focus is now on maximizing our chances. #Team{team_name}"
    ],
    "qualifying_1_win": [
        "Safely through {stage_abbr} and topped it with {result_detail}! The Mach 5 felt absolutely electric! #Team{team_name} giving me a rocket. On to Q2 with full confidence! #F1 #{race_name} #Qualifying #LeadingTheCharge 🚀",
        "P1 in {stage}! The Mach 5 is flying! Great first step in qualifying for #Team{team_name}. That lap felt sweet. More to come! #F1 #{race_name} #{stage_abbr} #PolePursuit 🔥",
        "Dominant run in {stage_abbr} to go through with {result_detail}! The Mach 5 is a beast! Thanks #Team{team_name}. Laser focus for Q2! #F1 #{race_name} #QualiKingInProgress 👑"
    ],
    "qualifying_1_good_result": [
        "Through to Q2! Solid job by the Mach 5 and #Team{team_name} in {stage_abbr}. The track is evolving fast. We're in the hunt! {result_detail} is a good base. #F1 #{race_name} #Qualifying #MovingOnUp 💨",
        "Q1 cleared! The Mach 5 handled the pressure well. Good strategic calls from #Team{team_name}. {result_detail} achieved, now for the next challenge! #F1 #{race_name} #{stage_abbr} #Advancing 💪",
        "Into Q2 we go! The Mach 5 felt strong out there for {result_detail}. That was a busy session, but #Team{team_name} navigated it perfectly. Let's keep climbing! #F1 #{race_name} #QualifyingSession 👍"
    ],
    "qualifying_1_difficult_race": [
        "Phew! That was a close one in {stage_abbr}! Made it through by the skin of our teeth, but the Mach 5 is in Q2! #Team{team_name} never gives up! We'll find more pace. #F1 #{race_name} #Qualifying #FightingSpirit 🙏",
        "Tough {stage} for us. Didn't quite have the pace we needed in the Mach 5 and unfortunately, we're out. Gutted for #Team{team_name}. We'll analyze and come back stronger for the race/next GP. #{race_name} #F1 #LearnAndRebuild 💔",
        "A real battle in {stage_abbr}! The Mach 5 wasn't comfortable, and we didn't make it through. Disappointing for #Team{team_name}, but we'll focus on what we can do from here. #{race_name} #F1 #QualifyingWoes 😔"
    ],
    "qualifying_1_dnf": [
        "Not on the first lap, not again! What a season! #F1 #{race_name} #Qualifying #FightingSpirit 🙏",
        "Tough {stage} for us.",
        "Not allowed to start {stage_abbr}! Why???. #{race_name} #F1 #QualifyingWoes 😔"
    ],
    "qualifying_2": [
        "What a round, {result_detail}. for now! #F1 #{race_name} #Qualifying",
        "Weather can be so unpredictable! We take {result_detail}. Looks like we might have to change our tires for Q3. #Team{team_name}"
    ],
    "qualifying_2_win": [
        "YES! P1 in {stage_abbr} with {result_detail}! The Mach 5 is on another level! #Team{team_name} you legends! Through to Q3 and ready to fight for POLE at #{race_name}! #F1 #Qualifying #TopSpotAgain 🌟",
        "Topped {stage} with {result_detail}! The Mach 5 felt absolutely hooked up. One more session to go for #Team{team_name}! The energy is incredible! #F1 #{race_name} #{stage_abbr} #PolePositionBound 🚀",
        "Another session, another P1 ({result_detail}) in {stage_abbr}! The Mach 5 is a dream today. #Team{team_name} is nailing the strategy. Let's finish the job in Q3! #F1 #{race_name} #QualifyingDominance 🏆"
    ],
    "qualifying_2_good_result": [
        "Into Q3! Fantastic lap with {result_detail}! The Mach 5 is in the Top 10 shootout! #Team{team_name} has given me a great car for #{race_name}. Time to unleash everything! #F1 #Qualifying #FinalShowdown 🔥",
        "Q2 done, and we're through with {result_detail}! The Mach 5 felt really strong. The atmosphere is electric. One more push for #Team{team_name}! #F1 #{race_name} #{stage_abbr} #GoingForGlory ✨",
        "YES! We made it to Q3 with {result_detail}! The Mach 5 was dancing out there. Huge effort from #Team{team_name}. Now for the exciting part! #F1 #{race_name} #QualifyingTop10 💪"
    ],
    "qualifying_2_difficult_race": [
        "That was a proper fight in {stage_abbr}! Scraped through to Q3, but the Mach 5 made it! {result_detail} isn't where we want to be, but we're in the hunt! #Team{team_name} will find a way! #F1 #{race_name} #Qualifying #NeverSayDie 😅",
        "Heartbreak in {stage}. Gave it everything in the Mach 5, but missed out on Q3 by the smallest margin. So frustrating for #Team{team_name}. We'll analyze and focus on a strong race from {result_detail}. #{race_name} #F1 #SoClose 💔",
        "A tough {stage_abbr} and that's as far as the Mach 5 goes today in qualifying. Disappointed for #Team{team_name}, but we'll give it everything from {result_detail} tomorrow. #{race_name} #F1 #QualifyingChallenge #RaceFocusNow 😔"
    ],
    "qualifying_2_dnf": [
        "Disapponting, just disappointing! At least this is a known issue and will be addressed. #Team{team_name}",
        "Heartbreak in {stage}. So frustrating for #Team{team_name}. We'll analyze and focus on a strong race from {result_detail}. #{race_name} #F1 #SoClose 💔",
        "A tough {stage_abbr} and that's as far as the Mach 5 goes today in qualifying. Disappointed for #Team{team_name}, but we'll give it everything from {result_detail} tomorrow. #{race_name} #F1 #QualifyingChallenge #RaceFocusNow 😔"
    ],
    "qualifying_3": [
        "Quali done. {result_detail}. We'll give it everything tomorrow for the race! #F1 #{race_name} #Qualifying",
        "That was intense! Secured {result_detail} for tomorrow's race. Focus is now on maximizing our chances. #Team{team_name}"
    ],
    "qualifying_3_win": [
        "POLE POSITION BABY! YES! {result_detail}! The Mach 5 was an absolute ROCKET! 🚀 #Team{team_name} you are legends! Front row for #{race_name} GP! Can't wait for tomorrow! #F1 #PolePosition #GoMachGo 🥇",
        "P1 ON THE GRID! {result_detail}! What a lap! The Mach 5 felt incredible. Massive thanks to #Team{team_name} for this weapon! Starting where we belong at #{race_name}! #F1 #QualifyingKing #PoleLap 🔥",
        "THAT'S POLE! {result_detail}! Unbelievable feeling to put the Mach 5 on the very front for #Team{team_name} at #{race_name}! The car was a dream. Now to convert it! #F1 #PoleSitter #DreamLap ✨"
    ],
    "qualifying_3_good_result": [
        "Fantastic result! {result_detail} on the grid for #{race_name} GP! The Mach 5 was flying in Q3. #Team{team_name} did an amazing job. Great spot to attack from tomorrow! #F1 #Qualifying #FrontRowsCalling 💨",
        "Excellent qualifying! Secured {result_detail} for #Team{team_name}. The Mach 5 felt really strong. We're in a prime position for a big points haul tomorrow at #{race_name}! #F1 #TopGridSlot #PodiumAim 💪",
        "Very happy with {result_detail} in Q3! The Mach 5 performed brilliantly. Big thanks to #Team{team_name} for their hard work. Ready to fight for it all tomorrow at #{race_name}! #F1 #QualiResult #RaceReady 🏎️"
    ],
    "qualifying_3_difficult_race": [
        "Q3 done, and we'll be starting {result_detail}. The Mach 5 had good pace, but it was incredibly tight out there. #Team{team_name} and I will be pushing hard for overtakes tomorrow at #{race_name}! #F1 #Qualifying #FightingChance 👊",
        "Okay, {result_detail} for tomorrow's race. Not exactly where we wanted the Mach 5 to be, but still in the top 10 and points are scored on Sunday! #Team{team_name} will cook up a great strategy for #{race_name}! #F1 #Quali #NeverGiveUp 🙏",
        "Finished Q3 in {result_detail}. A bit frustrating as I felt the Mach 5 had more, but the competition was fierce. #Team{team_name} is ready for a challenging race at #{race_name}. Let's make some moves! #F1 #QualifyingBattle #PushingForThePoints 💯"
    ],
    "qualifying_3_dnf": [
        "Q3 done, and we'll be starting 10th. The Mach 5 had good pace, but it was incredibly tight out there and we had an incident. #Team{team_name} and I will be pushing hard for more calculated overtakes tomorrow at #{race_name}! #F1 #Qualifying #FightingChance 👊",
        "Okay, 10th for tomorrow's race. Not exactly where we wanted the Mach 5 to be!  The mach 5 (and Bob) will return! #F1 #Quali #NeverGiveUp 🙏",
        "DNF! 10th! A bit frustrating we could not get a lap in. #Team{team_name} is ready for a challenging race at #{race_name}. Let's make some moves! #F1 #QualifyingBattle #PushingForThePoints 💯"
    ],
    "sprint_qualifying_1_win": [
        "Topped Sprint Qualifying 1 with {result_detail}! The Mach 5 is feeling feisty for this Sprint format at #{race_name}! Great start for #Team{team_name}. Let's carry this into SQ2! #F1Sprint #SQ1Winner #Mach5Fast 🚀",
        "P1 in SQ1 ({result_detail})! The Mach 5 loves these short, sharp sessions! #Team{team_name} on point. Ready for more Sprint action! #F1Sprint #{race_name} #LeadingTheWay 🔥",
        "Through SQ1 in style with {result_detail}! The Mach 5 is hooked up. #Team{team_name} is giving me a great car for this Sprint challenge! #F1Sprint #{race_name} #SprintKingInProgress 👑"
    ],
    "sprint_qualifying_1_good_result": [
        "Safely into SQ2 ({result_detail})! The Mach 5 felt good in that first Sprint Qualifying burst. #Team{team_name} making all the right calls. More pace to unlock! #F1Sprint #{race_name} #MovingOn 💨",
        "SQ1 cleared with {result_detail}! The Mach 5 is performing well under Sprint pressure. Good job #Team{team_name}. Let's see what SQ2 brings! #F1Sprint #{race_name} #SprintChallengeAccepted 💪",
        "Into the next part of Sprint Qualifying ({result_detail})! The Mach 5 handled that well. #Team{team_name} is ready for whatever this format throws at us! #F1Sprint #{race_name} #Focused 👍"
    ],
    "sprint_qualifying_1_difficult_race": [
        "Whew, that was a tight SQ1! Made it through ({result_detail}), but the Mach 5 had to work for it! #Team{team_name} will fine-tune for SQ2. Every session counts! #F1Sprint #{race_name} #CloseCall 🙏",
        "Tough first Sprint Qualifying session. The Mach 5 didn't have the edge, and we're out. Disappointed for #Team{team_name}. We'll focus on the main Qualifying later. #{race_name} #F1Sprint #LearnAndAdapt 💔",
        "A challenging SQ1, and that's our Sprint Qualifying done early. The Mach 5 struggled for pace. #Team{team_name} and I will reset for the main event. #{race_name} #F1Sprint #Frustrating 😔"
    ],
    "sprint_qualifying_2_win": [
        "P1 in SQ2 with {result_detail}! The Mach 5 is absolutely on it for this Sprint! #Team{team_name}, you beauty! One more shootout for the Sprint race pole at #{race_name}! #F1Sprint #SQ2Winner #AlmostThere 🌟",
        "Topped SQ2 ({result_detail})! The Mach 5 is flying high! #Team{team_name} is delivering a masterpiece. So pumped for SQ3! #F1Sprint #{race_name} #PoleFight 🚀",
        "Another P1 ({result_detail}) in SQ2! The Mach 5 feels unstoppable in this Sprint format. #Team{team_name} is on fire! Let's grab that Sprint pole! #F1Sprint #{race_name} #SprintDominance 🏆"
    ],
    "sprint_qualifying_2_good_result": [
        "Into SQ3 ({result_detail})! The Mach 5 is in the final shootout for the Sprint race! #Team{team_name} has given me a fantastic car for #{race_name}. Let's go for it! #F1Sprint #FinalSprintShowdown 🔥",
        "SQ2 done, and we're through ({result_detail})! The Mach 5 felt brilliant. The atmosphere is electric for this Sprint action. One last push with #Team{team_name}! #F1Sprint #{race_name} #GoingForSprintGlory ✨",
        "YES! We made it to SQ3 ({result_detail}) for the Sprint! The Mach 5 was a joy. Huge effort from #Team{team_name}. Time to shine! #F1Sprint #{race_name} #TopSprintContender 💪"
    ],
    "sprint_qualifying_2_difficult_race": [
        "That was a real dogfight in SQ2! Scraped into SQ3 ({result_detail}), but the Mach 5 is still in it! #Team{team_name} knows how to find that extra bit! #F1Sprint #{race_name} #HardFought 🙏",
        "So close in SQ2! The Mach 5 just missed out on SQ3. Gutted for #Team{team_name}. We'll start the Sprint from {result_detail} and fight hard for points! #{race_name} #F1Sprint #Almost 💔",
        "A tough SQ2 and our Sprint Qualifying ends here. The Mach 5 didn't have enough today. #Team{team_name} and I will give it our all in the Sprint race from {result_detail}. #{race_name} #F1Sprint #PointsHuntFromBehind 😔"
    ],
    "sprint_qualifying_3_win": [
        "SPRINT POLE! {result_detail}! YES! The Mach 5 was absolutely breathtaking! 🚀 #Team{team_name} you are incredible! Front of the grid for the Sprint race at #{race_name}! Let's get those points! #F1Sprint #SprintPole #GoMachGo 🥇",
        "P1 for the SPRINT RACE! {result_detail}! That lap felt perfect in the Mach 5. Huge thanks to #Team{team_name} for an amazing car! Ready to lead the charge at #{race_name}! #F1Sprint #SQWinner #SprintPoleLap 🔥",
        "POLE POSITION for the SPRINT! {result_detail}! What a thrill! The Mach 5 delivered when it mattered. #Team{team_name} nailed it! Starting P1 for the Sprint at #{race_name}! #F1Sprint #PoleSitter #DreamSprintStart ✨"
    ],
    "sprint_qualifying_3_good_result": [
        "Great Sprint Qualifying! {result_detail} on the grid for the Sprint race at #{race_name}! The Mach 5 was quick. #Team{team_name} did a fantastic job. Good position to fight for Sprint points! #F1Sprint #SQResult #FrontPack 💨",
        "Excellent SQ3! Secured {result_detail} for #Team{team_name} in the Sprint. The Mach 5 felt really competitive. We're aiming for a big haul of points in the Sprint at #{race_name}! #F1Sprint #TopSprintGridSlot #SprintPodiumPush 💪",
        "Very happy with {result_detail} in SQ3! The Mach 5 performed strongly. Big thanks to #Team{team_name}. Ready to attack in the Sprint race at #{race_name}! #F1Sprint #SQPodiumContender #SprintReady 🏎️"
    ],
    "sprint_qualifying_3_difficult_race": [
        "Sprint Qualifying complete, we'll start {result_detail} for the Sprint. The Mach 5 had decent pace, but it was super close. #Team{team_name} and I will be pushing for every point at #{race_name}! #F1Sprint #SQBattle #FightingForPoints 👊",
        "Okay, {result_detail} for the Sprint race. Hoped for a bit more with the Mach 5, but still in a good position to score. #Team{team_name} will have a sharp strategy for #{race_name}! #F1Sprint #SQ #NeverGiveUpSprint 🙏",
        "Finished SQ3 in {result_detail}. A bit of a mixed feeling as the Mach 5 felt good, but the times were tight. #Team{team_name} is ready for an action-packed Sprint at #{race_name}. Let's get 'em! #F1Sprint #SQChallenge #PushingForTheSprintPoints 💯"
    ],
    "sprint_race_win": [
        "SPRINT WINNERS! 🏆 YES! The Mach 5 was absolutely rapid in that 100km dash! Fantastic job by #Team{team_name}! Great points and a perfect Saturday! #F1Sprint #{race_name} #Winner #GoMachGo 🚀",
        "P1 in the Sprint! What a fantastic little race! The Mach 5 felt incredible from start to finish. Big up to #Team{team_name}! More points in the bag! #F1SprintVictory #{race_name} #ChampionSpirit ✨",
        "VICTORY in the SPRINT! 🍾 That was a fun blast! The Mach 5 was a rocket. Thanks #Team{team_name} for a perfect car and strategy! Love these Sprint races! #F1Sprint #{race_name}GP #Podium #Mach5Speed 💨",
        "SPRINT RACE CHAMPION! 🤩 The Mach 5 was untouchable! Great start, great pace. Thanks to everyone at #Team{team_name}! Those points feel good! #F1SprintWinner #{race_name} #RacingGlory 🎌",
        "Top step in the Sprint! 🥳 What a way to kick off the main action of the weekend! The Mach 5 handled beautifully. This is for #Team{team_name} and all the fans! #F1Sprint #{race_name}GP #SpeedDemon #Victory 🌟"
    ],
    "sprint_race_good_result": [
        "Solid points in the Sprint! 💪 The Mach 5 showed great pace. Happy with that result for #Team{team_name}. Good warm-up for the main event! #{race_name} #F1Sprint #PointsFinish 🏎️💨",
        "Good points haul in the Sprint race! The Mach 5 was strong. #Team{team_name} did a great job. Important points for the championship! #{race_name}GP #F1Sprint #Progress 📈",
        "Strong Sprint result! Proud of the effort from #Team{team_name}. The Mach 5 felt really competitive. Every point matters! Thanks for the cheers! #F1Sprint #{race_name} #PushingHard 🚀",
        "Really happy with that Sprint performance! Brought home some crucial points for #Team{team_name}. The track was exciting! Big thanks to the fans! #{race_name} #F1Sprint #Determined 💯",
        "A good day in the Sprint! The Mach 5 felt fantastic and #Team{team_name} nailed it. We'll take these points and focus on the GP! #F1Sprint #{race_name}GP #RacingSpirit 🔥"
    ],
    "sprint_race_difficult_race": [
        "Not the Sprint result we wanted. Gave it my all in the Mach 5, but it was a tough battle out there. We'll analyze and focus on the GP tomorrow with #Team{team_name}. #F1Sprint #{race_name} #NeverGiveUp 🙏",
        "Tough Sprint race. Pushed the Mach 5 hard, but couldn't make the progress I wanted. Disappointed, but we learn and move on to the main race. Thanks #Team{team_name}. #F1Sprint #{race_name} #LearnAndImprove 👊",
        "Challenging Sprint. We faced some tricky situations with the Mach 5. But that's racing! We'll use this experience for the GP. Appreciate the support! #Team{team_name} #F1Sprint #{race_name}GP #KeepFighting 🎌",
        "Well, that Sprint was a handful. The Mach 5 didn't quite have the edge we needed. But the spirit of #Team{team_name} is always to fight! All focus on tomorrow's Grand Prix. #{race_name} #F1Sprint #Onwards ❤️",
        "Tricky Sprint race for us. The Mach 5 felt a bit off, and we battled hard for every position. We'll regroup with #Team{team_name} and come out stronger for the GP! #F1Sprint #{race_name} #FullFocus 🎯"
    ],
    "sprint_race_dnf": [
        "Heartbreak in the Sprint. DNF is never easy, especially when the Mach 5 felt good. Something went wrong. Apologies to #Team{team_name}. We'll investigate and be ready for the GP. #F1Sprint #{race_name} #ToughBreak 💔",
        "That's an early end to our Sprint race. So frustrating for me and #Team{team_name}. Was pushing the Mach 5 and then it was over. We'll find out why. #F1Sprint #{race_name} #Resilience 🛠️",
        "DNF in the Sprint. Gutted for #Team{team_name}. The Mach 5 had more to give. We win and lose as a team. Focus now shifts to the Grand Prix. #F1Sprint #{race_name} #Unlucky 😔",
        "Unfortunately, our Sprint race was cut short. A real shame for #Team{team_name}. We'll analyze what happened to the Mach 5 and prepare for tomorrow. #F1Sprint #{race_name}GP #NeverSurrender ⚔️",
        "Sprint race over too soon due to an issue with the Mach 5. Disappointed for #Team{team_name} and our fans. We'll dig deep and aim for a big comeback in the GP! #F1Sprint #{race_name} #BounceBack 🚀"
    ],
    "reply_positive": [
        "Amazing! Thanks so much for the awesome support! Hearing that fires me up even more! #Team{team_name} #F1Family 🙏 LETS GOOO!",
        "Love the energy! 🚀 Your cheers make a massive difference out on track. So glad you enjoyed it! #Mach5Speed #BestFans",
        "That's what I'm talking about! 🤘 Thanks for believing in me and #Team{team_name}! We feel your passion! #F1 #{race_name}GP",
        "Fantastic! So happy to hear you enjoyed the action! We leave it all out there for you guys! #GoMachGo #F1Driver 💨",
        "Brilliant! Your support means the world to us at #Team{team_name}! Let's keep this positive wave rolling! #F1Community #ThankYou 🙌"
    ],
    "reply_negative": [
        "I hear you, and really appreciate you sharing your thoughts. It was a tough one for sure, but #Team{team_name} and I are already analyzing how to come back stronger! We won't give up! 💪 #F1Journey #KeepTheFaith",
        "Thanks for your honest feedback. Definitely not the result we aimed for with the Mach 5. We're learning from every lap and every race. Your support, even on difficult days, means a lot! #NeverGiveUp #Team{team_name} ❤️",
        "Yeah, that was a frustrating one, no doubt. We're as disappointed as you are. But the fight continues for #Team{team_name}! We'll channel this into motivation for the next one! Thanks for sticking with us! #F1 #Resilience 🙏",
        "Totally understand the frustration. We expect more from ourselves too. We'll take it on the chin, learn, and the Mach 5 will be back pushing for the front! Thanks for your continued passion! #Team{team_name} #OnwardsAndUpwards 🚀",
        "Appreciate you reaching out. It wasn't our day, but rest assured #Team{team_name} is already working hard to turn things around. Your belief in us is a huge motivator! #F1 #BetterDaysAhead ✨"
    ],
    "reply_neutral": [
        "Thanks for getting in touch! Always good to hear from the F1 fans! #Team{team_name} #F1Community 👍",
        "Appreciate the comment! Every voice helps us connect with our amazing supporters! #Mach5 #F1Fans 🏎️",
        "Cheers for the message! Hope you're enjoying the F1 season as much as I am! #GoMachGo #F1 🤘",
        "Noted! Thanks for sharing your perspective. We're always listening! #Team{team_name} #EngageF1 👀",
        "Thanks for reaching out! The passion of the F1 fans is what makes this sport so special! #F1Family #Mach5Speed 🙏"
    ]
}
