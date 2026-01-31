from analyses.five_forces import FiveForcesAnalysis


def test_sorting():
    analysis = FiveForcesAnalysis()

    # Data with mixed significance
    data = {
        "new_entrants": {
            "significance": "low",
            "description": "Desc Low",
            "impact": "Impact Low",
        },
        "supplier_power": {
            "significance": "high",
            "description": "Desc High 1",
            "impact": "Impact High 1",
        },
        "buyer_power": {
            "significance": "medium",
            "description": "Desc Med",
            "impact": "Impact Med",
        },
        "substitutes": {
            "significance": "high",
            "description": "Desc High 2",
            "impact": "Impact High 2",
        },
        "rivalry": {
            "significance": "low",
            "description": "Desc Low 2",
            "impact": "Impact Low 2",
        },
    }

    output = analysis.to_plain_text(data)
    print(output)

    # Check order
    lines = output.split("\n")
    headers = [line for line in lines if line.startswith("## ")]
    significances = [line for line in lines if line.startswith("**Significance:** ")]

    print("\nFound headers:", headers)
    print("Found significances:", significances)

    # We expect Highs, then Mediums, then Lows
    assert "High" in significances[0]
    assert "High" in significances[1]
    assert "Medium" in significances[2]
    assert "Low" in significances[3]
    assert "Low" in significances[4]

    print("\nSUCCESS: Forces are sorted correctly!")


if __name__ == "__main__":
    test_sorting()
