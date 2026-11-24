
import pytest
from load_scores import load_scores


# 테스트용 CSV 파일을 만드는 함수
def make_csv(tmp_path, content):
    path = tmp_path / "scores.csv"
    path.write_text(content, encoding="utf-8-sig")
    return path


# 1. 정상적인 성적 데이터
def test_normal_scores(tmp_path):
    path = make_csv(
        tmp_path,
        "name,score\n"
        "철수,90\n"
        "영희,85\n"
    )

    kept, skipped = load_scores(path)

    assert kept == [("철수", 90), ("영희", 85)]
    assert skipped == []


# 2. 경계값: 0점과 100점
def test_boundary_scores(tmp_path):
    path = make_csv(
        tmp_path,
        "name,score\n"
        "철수,0\n"
        "영희,100\n"
    )

    kept, skipped = load_scores(path)

    assert kept == [("철수", 0), ("영희", 100)]
    assert skipped == []


# 3. 범위를 벗어난 점수
def test_out_of_range(tmp_path):
    path = make_csv(
        tmp_path,
        "name,score\n"
        "철수,-1\n"
        "영희,101\n"
    )

    kept, skipped = load_scores(path)

    assert kept == []
    assert skipped == [
        (2, "철수,-1", "점수가 0~100 밖"),
        (3, "영희,101", "점수가 0~100 밖"),
    ]


# 4. 점수가 정수가 아닌 경우
def test_invalid_score(tmp_path):
    path = make_csv(
        tmp_path,
        "name,score\n"
        "철수,abc\n"
        "영희,85.5\n"
    )

    kept, skipped = load_scores(path)

    assert kept == []
    assert len(skipped) == 2
    assert skipped[0][2] == "점수가 정수가 아님"
    assert skipped[1][2] == "점수가 정수가 아님"


# 5. 이름이나 점수가 비어 있는 경우
def test_missing_values(tmp_path):
    path = make_csv(
        tmp_path,
        "name,score\n"
        ",90\n"
        "철수,\n"
    )

    kept, skipped = load_scores(path)

    assert kept == []
    assert skipped[0][2] == "이름이 비어 있음"
    assert skipped[1][2] == "점수가 비어 있음"


# 6. 열 개수가 잘못된 경우
def test_wrong_columns(tmp_path):
    path = make_csv(
        tmp_path,
        "name,score\n"
        "철수\n"
        "영희,90,A\n"
    )

    kept, skipped = load_scores(path)

    assert kept == []
    assert len(skipped) == 2
    assert all(
        row[2] == "열 개수가 2가 아님"
        for row in skipped
    )


# 7. 빈 줄은 기록하지 않는지 확인
def test_empty_lines(tmp_path):
    path = make_csv(
        tmp_path,
        "name,score\n"
        "\n"
        "철수,90\n"
    )

    kept, skipped = load_scores(path)

    assert kept == [("철수", 90)]
    assert skipped == []


# 8. 앞뒤 공백 제거
def test_whitespace(tmp_path):
    path = make_csv(
        tmp_path,
        "name,score\n"
        " 철수 , 90 \n"
    )

    kept, skipped = load_scores(path)

    assert kept == [("철수", 90)]
    assert skipped == []


# 9. 헤더만 있는 파일
def test_header_only(tmp_path):
    path = make_csv(tmp_path, "name,score\n")

    kept, skipped = load_scores(path)

    assert kept == []
    assert skipped == []


# 10. 파일이 존재하지 않는 경우
def test_file_not_found(tmp_path):
    path = tmp_path / "missing.csv"

    with pytest.raises(FileNotFoundError):
        load_scores(path)


# 11. 정상 데이터와 잘못된 데이터가 섞인 경우
def test_mixed_data(tmp_path):
    path = make_csv(
        tmp_path,
        "name,score\n"
        "철수,90\n"
        "영희,abc\n"
        "민수,100\n"
        "지수,105\n"
    )

    kept, skipped = load_scores(path)

    assert kept == [("철수", 90), ("민수", 100)]
    assert skipped == [
        (3, "영희,abc", "점수가 정수가 아님"),
        (5, "지수,105", "점수가 0~100 밖"),
    ]
