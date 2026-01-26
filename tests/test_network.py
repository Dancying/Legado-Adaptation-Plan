import os.path

import config
from utils import network


def test_proxyscotch(mode: str = "text") -> str | bytes:
    if mode == "text":  # 网页请求代理测试
        # r = network.fetch_data_by_proxyscotch("https://www.69shuba.com/txt/89532/40988851")
        # r = network.fetch_data_by_proxyscotch("https://twkan.com/txt/97359/53387395")
        # r = network.fetch_data_by_proxyscotch("https://69shux.co/txt/59854/30633557.html")
        r = network.fetch_data_by_proxyscotch("https://api.dancying.cn/legado/search22222")

    else:  # 图像请求代理测试
        r = network.fetch_data_by_proxyscotch("https://69shux.co/files/article/image/59/59854/59854s.jpg")
        with open(os.path.join(config.TEMP_DIR, "111.jpg"), mode="wb") as f:
            f.write(r)

    return r


if __name__ == '__main__':
    result = network.fetch_data_by_requests("https://api.dancying.cn/legado/search22222",)
    print(result.decode())
