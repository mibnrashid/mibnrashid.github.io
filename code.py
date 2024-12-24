def calculate_grade_range(grade):
    grade_mapping = {
        'A+': (93, 100),
        'A': (90, 92),
        'B+': (85, 89),
        'B': (80, 84),
        'C+': (75, 79),
        'C': (70, 74),
        'D+': (65, 69),
        'D': (60, 64),
        'F': (0, 59)
    }
    return grade_mapping.get(grade, (0, 0))  # Default to (0,0) if grade not found


def calculate_total(grades):
    weights = {
        'Writing1': 0.15,
        'Writing2': 0.15,
        'Midterm': 0.25,
        'Final Writing': 0.25,
        'Final Overall Reading-Vocabulary-Grammar': 0.20
    }
    
    total_min = 0
    total_max = 0
    
    for part, grade in grades.items():
        min_grade, max_grade = calculate_grade_range(grade)
        total_min += min_grade * weights[part]
        total_max += max_grade * weights[part]

    return total_min, total_max


def main():
    print("Enter your grades (A+, A, B+, etc.) for the following parts:")
    grades = {}
    
    for part in ['Writing1', 'Writing2', 'Midterm', 'Final Writing', 'Final Overall Reading-Vocabulary-Grammar']:
        grade = input(f"{part}: ").upper()
        grades[part] = grade
        
    min_total, max_total = calculate_total(grades)
    
    print(f"\nMinimum possible total: {min_total:.2f}")
    print(f"Maximum possible total: {max_total:.2f}")


main()
