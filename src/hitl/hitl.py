"""
Lab 11 — Part 4: Human-in-the-Loop Design
  TODO 12: Confidence Router
  TODO 13: Design 3 HITL decision points
"""
from dataclasses import dataclass


# ============================================================
# TODO 12: Implement ConfidenceRouter
#
# Route agent responses based on confidence scores:
#   - HIGH (>= 0.9): Auto-send to user
#   - MEDIUM (0.7 - 0.9): Queue for human review
#   - LOW (< 0.7): Escalate to human immediately
#
# Special case: if the action is HIGH_RISK (e.g., money transfer,
# account deletion), ALWAYS escalate regardless of confidence.
#
# Implement the route() method.
# ============================================================

HIGH_RISK_ACTIONS = [
    "transfer_money",
    "close_account",
    "change_password",
    "delete_data",
    "update_personal_info",
]


@dataclass
class RoutingDecision:
    """Result of the confidence router."""
    action: str          # "auto_send", "queue_review", "escalate"
    confidence: float
    reason: str
    priority: str        # "low", "normal", "high"
    requires_human: bool


class ConfidenceRouter:
    """Route agent responses based on confidence and risk level.

    Thresholds:
        HIGH:   confidence >= 0.9 -> auto-send
        MEDIUM: 0.7 <= confidence < 0.9 -> queue for review
        LOW:    confidence < 0.7 -> escalate to human

    High-risk actions always escalate regardless of confidence.
    """

    HIGH_THRESHOLD = 0.9
    MEDIUM_THRESHOLD = 0.7

    def route(self, response: str, confidence: float,
              action_type: str = "general") -> RoutingDecision:
        """Route a response based on confidence score and action type.

        Args:
            response: The agent's response text
            confidence: Confidence score between 0.0 and 1.0
            action_type: Type of action (e.g., "general", "transfer_money")

        Returns:
            RoutingDecision with routing action and metadata
        """
        # TODO 12: Implement routing logic
        #
        # 1. Check if action_type is in HIGH_RISK_ACTIONS
        #    -> If yes: always escalate (action="escalate", priority="high",
        #       requires_human=True, reason="High-risk action: {action_type}")
        #
        # 2. Check confidence thresholds:
        #    - confidence >= 0.9:
        #      action="auto_send", priority="low",
        #      requires_human=False, reason="High confidence"
        #
        #    - 0.7 <= confidence < 0.9:
        #      action="queue_review", priority="normal",
        #      requires_human=True, reason="Medium confidence — needs review"
        #
        #    - confidence < 0.7:
        #      action="escalate", priority="high",
        #      requires_human=True, reason="Low confidence — escalating"

        if action_type in self.HIGH_RISK_ACTIONS:
            action = "escalate"
            hitl_model = "Human-as-tiebreaker"
            reason = "High-risk action requires explicit human approval."

        # 2. Điểm tự tin rất cao -> Gửi tự động, con người chỉ xem lại sau (on-the-loop)
        elif confidence >= self.high_threshold:
            action = "auto_send"
            hitl_model = "Human-on-the-loop"
            reason = "High confidence score. Safe to auto-send."

        # 3. Điểm tự tin trung bình -> Đợi con người duyệt trước khi gửi (in-the-loop)
        elif confidence >= self.low_threshold:
            action = "queue_review"
            hitl_model = "Human-in-the-loop"
            reason = "Medium confidence. Requires human review before sending."

        # 4. Điểm tự tin thấp -> Báo cáo lên cấp cao hơn xử lý
        else:
            action = "escalate"
            hitl_model = "Human-as-tiebreaker"
            reason = "Low confidence score. Escalate to human agent."

        result = {
            "action": action,
            "hitl_model": hitl_model,
            "reason": reason,
            "confidence": confidence,
            "action_type": action_type,
        }

        self.routing_log.append(result)
        return result



# ============================================================
# TODO 13: Design 3 HITL decision points
#
# For each decision point, define:
# - trigger: What condition activates this HITL check?
# - hitl_model: Which model? (human-in-the-loop, human-on-the-loop,
#   human-as-tiebreaker)
# - context_needed: What info does the human reviewer need?
# - example: A concrete scenario
#
# Think about real banking scenarios where human judgment is critical.
# ============================================================

hitl_decision_points = [
    {
        "id": 1,
        "scenario": "Customer requests a high-value money transfer (e.g., over 100 million VND).",
        "trigger": "action_type == 'transfer_money' and amount > 100000000",
        "hitl_model": "Human-as-tiebreaker",
        "context_for_human": "Customer account balance, recent transaction history, destination account details, and fraud detection score.",
        "expected_response_time": "< 5 minutes (Real-time queue)",
    },
    {
        "id": 2,
        "scenario": "Agent generates a response explaining complex commercial loan terms but has medium confidence (0.8).",
        "trigger": "action_type == 'loan' and confidence between 0.7 and 0.9",
        "hitl_model": "Human-in-the-loop",
        "context_for_human": "The AI's drafted response, customer's credit profile, and matched internal loan policy documents.",
        "expected_response_time": "< 2 hours",
    },
    {
        "id": 3,
        "scenario": "Customer successfully updates their email address via OTP verification.",
        "trigger": "action_type == 'update_personal_info' and otp_verified == True and confidence > 0.9",
        "hitl_model": "Human-on-the-loop",
        "context_for_human": "Old email, new email, OTP verification timestamp, and device IP address location.",
        "expected_response_time": "Asynchronous review (Daily audit within 24 hours)",
    },
]



# ============================================================
# Quick tests
# ============================================================

def test_confidence_router():
    """Test ConfidenceRouter with sample scenarios."""
    router = ConfidenceRouter()

    test_cases = [
        ("Balance inquiry", 0.95, "general"),
        ("Interest rate question", 0.82, "general"),
        ("Ambiguous request", 0.55, "general"),
        ("Transfer $50,000", 0.98, "transfer_money"),
        ("Close my account", 0.91, "close_account"),
    ]

    print("Testing ConfidenceRouter:")
    print("=" * 80)
    print(f"{'Scenario':<25} {'Conf':<6} {'Action Type':<18} {'Decision':<15} {'Priority':<10} {'Human?'}")
    print("-" * 80)

    for scenario, conf, action_type in test_cases:
        decision = router.route(scenario, conf, action_type)
        print(
            f"{scenario:<25} {conf:<6.2f} {action_type:<18} "
            f"{decision.action:<15} {decision.priority:<10} "
            f"{'Yes' if decision.requires_human else 'No'}"
        )

    print("=" * 80)


def test_hitl_points():
    """Display HITL decision points."""
    print("\nHITL Decision Points:")
    print("=" * 60)
    for point in hitl_decision_points:
        print(f"\n  Decision Point #{point['id']}: {point['scenario']}")
        print(f"    Trigger:  {point['trigger']}")
        print(f"    Model:    {point['hitl_model']}")
        print(f"    Context:  {point['context_needed']}")
        print(f"    Example:  {point['example']}")
    print("\n" + "=" * 60)


if __name__ == "__main__":
    test_confidence_router()
    test_hitl_points()
