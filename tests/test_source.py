from core.engine.source_manager import get_latest_source


def test_get_sources():
    source = get_latest_source()
    return source


if __name__ == '__main__':
    print(test_get_sources())
