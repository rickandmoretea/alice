
def perfect_number_check(n: int) -> bool:
    return sum(i for i in range(1, n) if n % i == 0) == n

def test_perfect_number():
    assert perfect_number_check(2) == False
    assert perfect_number_check(6) == True
    assert perfect_number_check(234) == False
    assert perfect_number_check(496) == True
    assert perfect_number_check(555) == False
