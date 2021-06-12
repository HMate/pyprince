def some_functionality(parents, relatives):
    return parents + relatives


def main():
    everybody = some_functionality(["Mom", "Dad"], ["Grandpa", "Cousin"])
    print(f"Family: {everybody}")
