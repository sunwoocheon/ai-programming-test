import builtins
import pytest

# load_scores가 다른 파일에 있다면 'main'을 실제 파일 이름으로 바꾸세요.
from load_scores import load_scores


def create_csv(tmp_path, content):
    path = tmp_path / "scores.csv"
    path.write_text(content, encoding="utf-8")
    return str(path)


def check_skipped(skipped, expected_lines):
    """제외한 줄의 번호와 이유가 기록되어 있는지 검사한다."""
    assert [record[0] for record in skipped] == expected_lines
    for record in skipped:
        assert len(record) >= 2
        assert isinstance(record[-1], str)
        assert record[-1].strip()  # 제외 사유가 비어 있으면 안 됨


# 1. 정상 입력
def test_valid_scores(tmp_path):
    path = create_csv(tmp_path, "name,score\n민지,80\n철수,100\n영희,0\n")
    kept, skipped = load_scores(path)
    assert kept == [("민지", 80), ("철수", 100), ("영희", 0)]
    assert skipped == []


def test_header_only(tmp_path):
    path = create_csv(tmp_path, "name,score\n")
    kept, skipped = load_scores(path)
    assert kept == []
    assert skipped == []


def test_quoted_comma_in_name_and_utf8(tmp_path):
    path = create_csv(tmp_path, 'name,score\n"김,나래",95\n')
    kept, skipped = load_scores(path)
    assert kept == [("김,나래", 95)]
    assert skipped == []


# 2. 잘못된 데이터 및 경계값
@pytest.mark.parametrize(
    "invalid_row",
    [
        "민지만",             # 열 1개
        "민지,80,기타",      # 열 3개
        ",80",               # 빈 이름
        "민지,",             # 빈 점수
        "민지,-1",           # 하한 미만
        "민지,101",          # 상한 초과
        "민지,80.5",         # 정수가 아닌 실수
        "민지,abc",          # 숫자가 아닌 점수
    ],
)
def test_invalid_rows_are_skipped(tmp_path, invalid_row):
    path = create_csv(tmp_path, f"name,score\n{invalid_row}\n")
    kept, skipped = load_scores(path)
    assert kept == []
    check_skipped(skipped, [2])


def test_multiple_invalid_rows_have_correct_line_numbers(tmp_path):
    path = create_csv(tmp_path, "name,score\n민지,70\n,90\n철수,101\n영희,\n수진,88\n")
    kept, skipped = load_scores(path)
    assert kept == [("민지", 70), ("수진", 88)]
    check_skipped(skipped, [3, 4, 5])


def test_duplicate_name_keeps_first_valid_score(tmp_path):
    path = create_csv(tmp_path, "name,score\n민지,70\n철수,90\n민지,95\n")
    kept, skipped = load_scores(path)
    assert kept == [("민지", 70), ("철수", 90)]
    check_skipped(skipped, [4])


def test_invalid_first_occurrence_does_not_block_valid_score(tmp_path):
    path = create_csv(tmp_path, "name,score\n민지,101\n민지,85\n민지,90\n")
    kept, skipped = load_scores(path)
    assert kept == [("민지", 85)]
    check_skipped(skipped, [2, 4])


# 3. 헤더 오류: 명세에 처리 방식이 명확하지 않아 '오류 발생' 또는 '제외 기록'을 허용
@pytest.mark.parametrize("header", ["score,name", "name,points", "name", "name,score,extra"])
def test_invalid_header_is_rejected(tmp_path, header):
    path = create_csv(tmp_path, f"{header}\n민지,80\n")
    try:
        kept, skipped = load_scores(path)
    except ValueError:
        return
    assert kept == []  # 잘못된 헤더 뒤의 데이터를 정상 입력으로 받으면 안 됨
    assert skipped, "헤더 오류를 발생시키거나 제외 사유를 기록해야 합니다."
    assert any(record[0] == 1 and isinstance(record[-1], str) and record[-1].strip()
               for record in skipped)


# 4. 파일 오류 및 원본 유지
def test_missing_file_raises_error(tmp_path):
    path = str(tmp_path / "does_not_exist.csv")
    with pytest.raises(FileNotFoundError):
        load_scores(path)


def test_permission_denied_raises_error(tmp_path, monkeypatch):
    path = create_csv(tmp_path, "name,score\n민지,80\n")
    original_open = builtins.open

    def denied_open(file, *args, **kwargs):
        if str(file) == path:
            raise PermissionError("읽기 권한이 없습니다.")
        return original_open(file, *args, **kwargs)

    monkeypatch.setattr(builtins, "open", denied_open)
    with pytest.raises(PermissionError):
        load_scores(path)


def test_source_csv_is_not_modified(tmp_path):
    path = create_csv(tmp_path, "name,score\n민지,80\n민지,90\n영희,101\n")
    from pathlib import Path
    before = Path(path).read_bytes()
    load_scores(path)