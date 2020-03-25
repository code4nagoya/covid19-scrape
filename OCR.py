from PIL import Image
import pyocr

# OCRエンジンの取得
tools = pyocr.get_available_tools()
tool = tools[0]

# 原稿画像の読み込み
img_org = Image.open("./data/subject.jpg")
img_rgb = img_org.convert("RGB")
pixels = img_rgb.load()

# 原稿画像加工（黒っぽい色以外は白=255,255,255にする）
c_max = 169
for j in range(img_rgb.size[1]):
    for i in range(img_rgb.size[0]):
        if (pixels[i, j][0] > c_max or pixels[i, j][1] > c_max or
                pixels[i, j][0] > c_max):
            pixels[i, j] = (255, 255, 255)

# OCRを実行する
builder = pyocr.builders.TextBuilder()
result = tool.image_to_string(img_rgb, lang="jpn", builder=builder)

print(result)