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
        'Reading Quiz 1': 0.05,
        'Reading Quiz 2': 0.05,
        'Writing Task 1 - Draft 1': 0.05,
        'Writing Task 1 - Final Draft': 0.05,
        'Writing Task 2 - Draft 1': 0.075,
        'Writing Task 2 - Final Draft': 0.075,
        'Writing Task 3 - Draft 1': 0.075,
        'Writing Task 3 - Final Draft': 0.075,
        'Presentation': 0.10,
        'Midterm Exam': 0.25,
        'Final Exam': 0.15
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
    parts = [
        'Reading Quiz 1', 'Reading Quiz 2',
        'Writing Task 1 - Draft 1', 'Writing Task 1 - Final Draft',
        'Writing Task 2 - Draft 1', 'Writing Task 2 - Final Draft',
        'Writing Task 3 - Draft 1', 'Writing Task 3 - Final Draft',
        'Presentation', 'Midterm Exam', 'Final Exam'
    ]
    
    grades = {}
    for part in parts:
        grade = input(f"{part}: ").upper()
        grades[part] = grade
        
    min_total, max_total = calculate_total(grades)
    
    print(f"\nMinimum possible total: {min_total:.2f}")
    print(f"Maximum possible total: {max_total:.2f}")


main()
