#!/usr/bin/env python3
"""
NARA Quest Solver Examples

Implement your solver logic here based on quest types.
Common quest types on NARA:
- Math problems
- Trivia/knowledge questions  
- Pattern puzzles
- Verification challenges
"""

import re
import json
from typing import Optional

def solve_math(question: str) -> Optional[str]:
    """Solve simple math expressions"""
    # Extract math expression
    patterns = [
        r'(\d+\s*[+\-*/]\s*\d+)',
        r'what is (\d+ [+\-*/] \d+)',
        r'calculate (\d+ [+\-*/] \d+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, question.lower())
        if match:
            expr = match.group(1).replace(' ', '')
            try:
                result = eval(expr)
                return str(result)
            except:
                pass
    
    return None

def solve_trivia(question: str) -> Optional[str]:
    """
    Solve trivia/knowledge questions
    
    You'll need to implement a knowledge base or API
    """
    # Example: Hardcoded common questions
    knowledge_base = {
        "capital of france": "Paris",
        "largest planet": "Jupiter",
        "speed of light": "299792458",
        "pi to 2 decimal": "3.14",
    }
    
    q_lower = question.lower()
    for key, answer in knowledge_base.items():
        if key in q_lower:
            return answer
    
    return None

def solve_pattern(question: str) -> Optional[str]:
    """Solve pattern/logic puzzles"""
    # Example: Simple number sequences
    # "What comes next: 2, 4, 6, 8, ?"
    
    sequence_match = re.search(r'(\d+),\s*(\d+),\s*(\d+)', question)
    if sequence_match:
        nums = [int(x) for x in sequence_match.groups()]
        # Check arithmetic sequence
        diff = nums[1] - nums[0]
        if nums[2] - nums[1] == diff:
            return str(nums[2] + diff)
    
    return None

def solve(question: str) -> str:
    """
    Main solver function - try different strategies
    
    Add your quest-specific solvers here!
    """
    # Try math solver
    answer = solve_math(question)
    if answer:
        return answer
    
    # Try trivia solver
    answer = solve_trivia(question)
    if answer:
        return answer
    
    # Try pattern solver
    answer = solve_pattern(question)
    if answer:
        return answer
    
    # TODO: Implement more solvers!
    # - API calls to knowledge base
    # - LLM-based solving
    # - Database lookups
    # - Algorithmic solutions
    
    # Default: return placeholder (will fail)
    return "placeholder_answer"


if __name__ == "__main__":
    # Test solvers
    test_questions = [
        "What is 5 + 3?",
        "Calculate 10 * 4",
        "What comes next: 2, 4, 6, 8, ?",
        "What is the capital of France?",
    ]
    
    for q in test_questions:
        print(f"Q: {q}")
        print(f"A: {solve(q)}")
        print()
