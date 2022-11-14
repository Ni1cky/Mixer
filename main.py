import os.path

from PIL import Image, UnidentifiedImageError

from config import PART_WIDTH, PART_HEIGHT, PICTURES_DIRECTORY


def images_converted_to_colors() -> bool:
    return os.path.exists(".saved/converted.txt")


def using_previous() -> bool:
    if images_converted_to_colors():
        choice = input(
            'Использовать загруженные ранее картинки? ("Да" | "Нет")\n'
        ).lower()
        if choice == "да":
            return True
        elif choice != "нет":
            print('Ввод не обработан. Я считаю, что это было "Нет"')
    return False


def get_av_color(image_path, number, resize=True):
    img = Image.open(image_path)
    if resize:
        total_pixels = PART_WIDTH * PART_HEIGHT
        img = img.resize((PART_WIDTH, PART_HEIGHT))
        img.save(f".saved/{number}.{image_path.split('.')[-1]}")
    else:
        total_pixels = img.height * img.height
    pixels = img.load()
    av_r = av_g = av_b = 0
    for i in range(PART_HEIGHT):
        for j in range(PART_WIDTH):
            r, g, b, *smth = pixels[j, i]
            av_r += r
            av_g += g
            av_b += b
    img.close()
    return av_r // total_pixels, av_g // total_pixels, av_b // total_pixels


def images_to_av_colors():
    av_colors = []
    for file_name in os.listdir(PICTURES_DIRECTORY):
        name, ext, *smth = file_name.split('.')
        if not smth and ext == "jpg" or ext == "png":
            av_color = get_av_color(f"{PICTURES_DIRECTORY}{file_name}", len(av_colors))
            av_colors.append(av_color)
    return av_colors


def save_for_future(colors):
    converted = open(".saved/converted.txt", "w")
    for color in colors:
        converted.write(" ".join(map(str, color)) + "\n")
    converted.close()


def read_last_saved():
    converted = open(".saved/converted.txt", "r")
    colors = list(map(lambda c: tuple(map(int, c.split())), converted.readlines()))
    converted.close()
    return colors


def get_rect_av_color(start_i, start_j, pixels):
    av_r = av_g = av_b = 0
    cnt = 0
    for i in range(start_i, start_i + PART_HEIGHT):
        for j in range(start_j, start_j + PART_WIDTH):
            try:
                r, g, b, *smth = pixels[j, i]
                av_r += r
                av_g += g
                av_b += g
                cnt += 1
            except IndexError:
                continue
    return av_r // cnt, av_g // cnt, av_b // cnt


def distance(color_1, color_2):
    return (
                   (color_1[0] - color_2[0]) ** 2 +
                   (color_1[1] - color_2[1]) ** 2 +
                   (color_1[2] - color_2[2]) ** 2
           ) ** 0.5


def nearest(cur_rect_av_color, colors):
    min_dist = 450
    for color_ind in range(len(colors)):
        dist = distance(colors[color_ind], cur_rect_av_color)
        if dist < min_dist:
            min_dist = dist
            min_ind = color_ind
    return min_ind


def insert_part(nearest_img_ind, start_i, start_j, pixels):
    try:
        img = Image.open(f".saved/{nearest_img_ind}.jpg")
    except FileNotFoundError:
        img = Image.open(f".saved/{nearest_img_ind}.png")
    pixels_to_insert = img.load()
    for i in range(PART_HEIGHT):
        for j in range(PART_WIDTH):
            try:
                pixels[start_j + j, start_i + i] = pixels_to_insert[j, i]
            except IndexError:
                continue
    img.close()


def mix_picture(pic_path, colors):
    try:
        picture = Image.open(pic_path)
    except FileNotFoundError:
        print("Картинка не существует")
        return False
    except UnidentifiedImageError:
        print("Не удалось загрузить картинку. Возможно, это не картинка")
        return False
    pixels = picture.load()

    for i in range(0, picture.height, PART_HEIGHT):
        for j in range(0, picture.width, PART_WIDTH):
            cur_rect_av_color = get_rect_av_color(i, j, pixels)
            nearest_img_ind = nearest(cur_rect_av_color, colors)
            insert_part(nearest_img_ind, i, j, pixels)
    picture.save(f"result.{pic_path.split('.')[-1]}")
    return True


def main():
    if using_previous():
        colors = read_last_saved()
    else:
        print(f"Используемые картинки должны быть в папке {PICTURES_DIRECTORY}")
        input('"Enter" по готовности\n')
        print("Подготовка...")
        colors = images_to_av_colors()
        save_for_future(colors)
    file_name = input("Путь до картинки, которая превратится в мозаику: ")
    print("Создание мозайки...")
    res = mix_picture(file_name, colors)
    if res:
        print(f"Результат: result.{file_name.split('.')[-1]}")


if __name__ == '__main__':
    main()
