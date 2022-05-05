import os
import random
import datetime
import sys


NUM_QUESTIONS = 30


def cut_prefix(line: str) -> str:
    return line[3:].strip()


class Question:
    def __init__(self, question_struct) -> None:
        self.question_id = cut_prefix(question_struct[0])
        self.question_text = cut_prefix(question_struct[1])
        self.question_list = list(
            enumerate(list(map(lambda x: cut_prefix(x), question_struct[2:]))))
        random.shuffle(self.question_list)
        self.user_choice: int = None
        self.correctness: bool = None

    def __str__(self) -> str:
        return """问题：{}
A. {}
B. {}
C. {}
D. {}
""".format(self.question_text,
           *list(map(lambda x: x[1], self.question_list)))

    def set_user_choice(self, user_choice: str):
        self.user_choice = "abcd".find(user_choice)
        self.correctness = self.question_list[self.user_choice][0] == 0

    def get_wrong_choice(self):
        if self.correctness == True:
            return None
        return "ABCD"[self.user_choice]

    def get_correct_choice(self):
        correct_anser_tuple = next(
            filter(lambda x: x[1][0] == 0, list(enumerate(self.question_list))))
        choice_numerical = correct_anser_tuple[0]
        choice_alphabetical = "ABCD"[choice_numerical]
        return choice_alphabetical


def get_resource_path(relative_path):
    """
    Provide compatibility for Pyinstaller's relative paths
    """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


def get_question_list() -> list[Question]:
    question_base = open(get_resource_path("A类题库(v20211022).txt"), "r")
    status = "none"
    question_struct = []
    question_list = []

    for line in question_base.readlines():
        if status == "none":
            question_struct.clear()

        if line.startswith("[I]"):
            status = "building"
        elif line.startswith("[P]"):
            status = "save_question"

        if status == "building":
            question_struct.append(line)
        elif status == "save_question":
            question_list.append(Question(question_struct))
            status = "none"

    question_base.close()
    return question_list


def get_user_choice_from_terminal():
    user_choice = input("选项：").strip().lower()
    if len(user_choice) != 1 or user_choice not in "abcd":
        return None
    return user_choice


def write_shuati_results(question_list: list[Question], user_duration: str, result_filename: str) -> None:
    result_path = os.path.dirname(result_filename)
    if not os.path.exists(result_path):
        os.mkdir(result_path)

    with open(result_filename, "w") as out_file:
        out_file.write(
            "结果：{}/{}，耗时：{}\n".format(
                num_correct_answers(question_list),
                NUM_QUESTIONS,
                user_duration
            )
        )

        out_file.write(
            "\n====错题记录============================================\n")
        for wrongly_answered in filter(lambda q: q.correctness == False, question_list):
            out_buf = [
                "\n",
                str(wrongly_answered),
                "\n你的选项：{}\t正确选项：{}\n\n".format(
                    wrongly_answered.get_wrong_choice(),
                    wrongly_answered.get_correct_choice()
                )
            ]
            out_file.writelines(out_buf)

        out_file.write(
            "\n\n====正解记录============================================\n")
        for correctly_answered in filter(lambda q: q.correctness == True, question_list):
            out_buf = [
                "\n",
                str(correctly_answered),
                "\n你的选项：{}\t正确选项：{}\n\n".format(
                    correctly_answered.get_correct_choice(),
                    correctly_answered.get_correct_choice()
                )
            ]
            out_file.writelines(out_buf)


def num_correct_answers(question_list: list[Question]):
    return len(list(filter(lambda q: q.correctness, question_list)))


def main():
    question_list = get_question_list()
    random.shuffle(question_list)
    shuffled_questions: list[Question] = question_list[:NUM_QUESTIONS]

    start_time = datetime.datetime.now()
    cnt = 1

    for question in shuffled_questions:
        print("\n[{}/{}]".format(cnt, NUM_QUESTIONS), question)
        cnt += 1
        while True:
            user_choice = get_user_choice_from_terminal()
            if user_choice is not None:
                break
            else:
                print("输入不正确，请重新输入选项")
        question.set_user_choice(user_choice)

    end_time = datetime.datetime.now()
    user_duration = str(end_time - start_time).split(".")[0]
    ftime = end_time.strftime("%Y%m%d-%H%M%S")
    result_filename = os.path.join(
        get_resource_path(""), "做题记录", ftime + "做题记录.txt")
    write_shuati_results(shuffled_questions, user_duration, result_filename)
    print("结果：{}/{}, 耗时：{}, 详细记录已保存至 {}".
          format(
              num_correct_answers(shuffled_questions),
              NUM_QUESTIONS,
              user_duration,
              result_filename)
          )


if __name__ == "__main__":
    main()
