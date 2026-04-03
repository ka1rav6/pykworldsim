class Goal:
    """Represents a personal goal with a type and priority."""

    ValidGoalTypes = {
        "GetJob", "GetPromotion", "MakeFriends", "FindPartner",
        "ImproveSkills", "EarnMoney", "IncreaseStatus", "MoveCity",
        "StartFamily", "BuildBusiness", "SocializeMore", "FindPurpose"
    }

    def __init__(self, GoalType: str, Priority: float = 0.5):
        if GoalType not in self.ValidGoalTypes:
            raise ValueError(f"GoalType '{GoalType}' is not valid. Choose from: {sorted(self.ValidGoalTypes)}")
        if not (0.0 <= Priority <= 1.0):
            raise ValueError("Priority must be between 0.0 and 1.0")
        self.GoalType = GoalType
        self.Priority = Priority
        self.Progress = 0.0
        self.Achieved = False
        self.YearAchieved = None

    def UpdateProgress(self, Delta: float):
        self.Progress = max(0.0, min(1.0, self.Progress + Delta))
        if self.Progress >= 1.0 and not self.Achieved:
            self.Achieved = True
            return True
        return False

    def __repr__(self):
        Status = "✓" if self.Achieved else f"{self.Progress:.0%}"
        return f"Goal({self.GoalType}, priority={self.Priority:.1f}, progress={Status})"
