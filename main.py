import os.path


def images_converted_to_colors() -> bool:
    if os.path.exists("/.saved/converted.txt"):
        return True
    return False


def main():
    pass


if __name__ == '__main__':
    main()
