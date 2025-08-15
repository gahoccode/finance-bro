#!/usr/bin/env python
from .crew import FinancialHealthCrew


def run():
    """
    Run the Financial Health Analysis crew.
    """
    inputs = {
        'stock_symbol': 'Default analysis for loaded financial data'
    }
    
    crew = FinancialHealthCrew()
    result = crew.crew().kickoff(inputs=inputs)
    return result


if __name__ == "__main__":
    run()