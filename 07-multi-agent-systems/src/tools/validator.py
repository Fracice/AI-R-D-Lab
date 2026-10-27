import math


ALLOWED_METRICS = {
    "units_sold",
    "revenue",
    "gross_profit",
    "margin_percentage",
}


def validate_recommendations(recommendations, verified_facts):
    """
    Validate structured recommendations against verified business facts.

    Product names, metric names and expected values are retrieved dynamically
    from verified_facts. No product names or metric values are hard-coded.
    """
    issues = []

    if not isinstance(recommendations, dict):
        return ["Recommendations must be a JSON object."]

    items = recommendations.get("recommendations")

    if not isinstance(items, list):
        return ["The 'recommendations' field must be a list."]

    if not items:
        return ["At least one recommendation is required."]

    verified_products = verified_facts.get("products", {})

    for index, item in enumerate(items, start=1):
        prefix = f"Recommendation {index}"

        if not isinstance(item, dict):
            issues.append(f"{prefix} must be an object.")
            continue

        # Check the required recommendation fields.
        required_fields = {
            "recommendation",
            "priority",
            "supporting_metrics",
            "rationale",
            "assumptions",
        }

        missing_fields = required_fields - item.keys()

        if missing_fields:
            issues.append(
                f"{prefix} is missing fields: "
                + ", ".join(sorted(missing_fields))
            )

        if not isinstance(item.get("recommendation"), str) or not (
            item.get("recommendation", "").strip()
        ):
            issues.append(
                f"{prefix}: 'recommendation' must be a non-empty string."
            )

        priority = item.get("priority")
        if (
            not isinstance(priority, int)
            or isinstance(priority, bool)
            or priority < 1
        ):
            issues.append(
                f"{prefix}: 'priority' must be a positive integer."
            )

        if not isinstance(item.get("rationale"), str):
            issues.append(
                f"{prefix}: 'rationale' must be a string."
            )

        if not isinstance(item.get("assumptions"), list) or not all(
            isinstance(value, str)
            for value in item.get("assumptions", [])
        ):
            issues.append(
                f"{prefix}: 'assumptions' must be a list of strings."
            )

        supporting_metrics = item.get("supporting_metrics")

        if not isinstance(supporting_metrics, list):
            issues.append(
                f"{prefix}: 'supporting_metrics' must be a list."
            )
            continue

        for metric_index, reference in enumerate(
            supporting_metrics, start=1
        ):
            metric_prefix = (
                f"{prefix}, supporting metric {metric_index}"
            )

            if not isinstance(reference, dict):
                issues.append(
                    f"{metric_prefix} must be an object."
                )
                continue

            product_name = reference.get("product")
            metric_name = reference.get("metric")
            reported_value = reference.get("value")

            if not isinstance(product_name, str):
                issues.append(
                    f"{metric_prefix}: product must be a string."
                )
                continue

            if product_name not in verified_products:
                issues.append(
                    f"{metric_prefix}: unknown product '{product_name}'."
                )
                continue

            if metric_name not in ALLOWED_METRICS:
                issues.append(
                    f"{metric_prefix}: unsupported metric '{metric_name}'."
                )
                continue

            product_facts = verified_products[product_name]

            if metric_name not in product_facts:
                issues.append(
                    f"{metric_prefix}: metric '{metric_name}' is not "
                    f"available for product '{product_name}'."
                )
                continue

            expected_value = product_facts[metric_name]

            if (
                isinstance(reported_value, bool)
                or not isinstance(reported_value, (int, float))
                or not math.isfinite(reported_value)
            ):
                issues.append(
                    f"{metric_prefix}: value must be a finite number."
                )
                continue

            if isinstance(expected_value, (int, float)):
                matches = math.isclose(
                    reported_value,
                    expected_value,
                    rel_tol=0,
                    abs_tol=0.01,
                )
            else:
                matches = reported_value == expected_value

            if not matches:
                issues.append(
                    f"{metric_prefix}: reported value {reported_value} "
                    f"does not match verified value {expected_value} "
                    f"for {product_name}.{metric_name}."
                )

    return issues


if __name__ == "__main__":
    sample_facts = {
        "products": {
            "Keyboard": {
                "units_sold": 150,
                "revenue": 9000,
                "gross_profit": 5250,
                "margin_percentage": 58.33,
            },
            "Mouse": {
                "units_sold": 180,
                "revenue": 6300,
                "gross_profit": 4140,
                "margin_percentage": 65.71,
            },
        }
    }

    test_recommendations = {
        "recommendations": [
            {
                "recommendation": "Review Mouse pricing.",
                "priority": 1,
                "supporting_metrics": [
                    {
                        "product": "Mouse",
                        "metric": "margin_percentage",
                        "value": 65.71,
                    },
                    {
                        "product": "Keyboard",
                        "metric": "units_sold",
                        "value": 250,
                    },
                ],
                "rationale": "Use verified metrics to inform the review.",
                "assumptions": [],
            }
        ]
    }

    validation_issues = validate_recommendations(
        test_recommendations,
        sample_facts,
    )

    print("Validation issues:")
    for issue in validation_issues:
        print("-", issue)