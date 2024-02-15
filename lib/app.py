from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base
import inquirer
from models.player import Player, HighScore, Wordle
from models.seed import Word
from colorama import Fore 
from models.player import LetterLogic
from typing import List

engine = create_engine('sqlite:///wordle.db')
Base = declarative_base()

Base.metadata.create_all(engine)

def main():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        def main_menu():
            questions = [
                inquirer.List(
                    "first_menu",
                    message="Please Select: ",
                    choices=[
                        "Sign in",
                        "Create Player",
                        "Exit"
                    ]
                )
            ]
            response = inquirer.prompt(questions)
            if response["first_menu"] == "Sign in":
                sign_in(session)
            elif response["first_menu"] == "Create Player":
                create_player(session)
            elif response["first_menu"] == "Exit":
                exit()
            else:
                print("Invalid Choice")

        def create_player(session):
            name = input("Enter Your Name: ")
            existing_player = session.query(Player).filter(Player.name == name).first()
            if existing_player:
                print(f"{name} Already Exists. Please Sign In.")
            else:
                new_player = Player(name=name)
                session.add(new_player)
                session.commit()
                print(f"Player '{name}' has been created successfully.")
                main_menu() 
            
        
        def sign_in(session):
            name = input("Enter Your Name: ")
            player_instance = session.query(Player).filter(Player.name == name).first()
            if player_instance:
                print(f'Welcome {player_instance.name}')
                second_menu(session, player_instance)
            else:
                print("Player Not Found. Please Create new Player.")

        

        
            

        def exit():
            return
        

        def second_menu(session, player_instance):
            questions = [
                inquirer.List(
                    "second_menu",
                    message="Please Select: ",
                    choices=[
                        "Play",
                        "High Scores",
                        "Edit Player",
                        "Exit"
                    ]
                )
            ]
            response = inquirer.prompt(questions)
            if response["second_menu"] == "Play":
                play(session, player_instance)
            elif response["second_menu"] == "High Scores":
                high_scores(session, player_instance)
            elif response["second_menu"] == "Edit Player":
                edit_player(session, player_instance)
            elif response["second_menu"] == "Exit":
                exit()


        def play(session, player_instance):
            secret_word = Word.get_random_word(session)
            wordle = Wordle(secret=secret_word)

            while wordle.playing_game: 
                x = input("Type your guess: ")
                if len(x) != 5: 
                    print(Fore.RED + "Please enter a 5 letter word" + Fore.RESET)
                    continue
                wordle.attempt(x)
                display_results(wordle )
                results = wordle.guesses(x)
                print(*results, sep="\n")
            if wordle.won_game:
                    print("You guessed it! You're score is " + str(len(wordle.attempts)))
                    player_instance.record_high_score(len(wordle.attempts))
                    session.commit()
            else: 
                print("You lost. The word was " + wordle.secret)

        def display_results(wordle: Wordle):
            print("\nYour results so far ...")
            print(f"You have {wordle.attempts_left} attempts left")

            lines =[]

            for word in wordle.attempts:
                result = wordle.guesses(word)
                colored_results = result_to_color(result)
                lines.append(colored_results)
            for _ in range(wordle.attempts_left):
                lines.append(" ".join(["_"] * wordle.WORD_LENGTH))
            print("\n".join(lines))
            create_board(lines)
            

        def result_to_color(result: List[LetterLogic]):
            result_color = []
            for letter in result:
                if letter.in_position:
                    color = Fore.GREEN
                elif letter.in_word:
                    color = Fore.YELLOW
                else:
                    color = Fore.WHITE
                colored_letter = color + letter.character + Fore.RESET
                result_color.append(colored_letter)
            return "".join(result_color)



        def create_board(lines: List[str], size: int=9, pad: int =1):
            content_length = size + pad * 2
            top_border = "┌" + "─" * content_length + "┐"
            bottom_border = "└" + "─" * content_length + "┘"
            space = " " * pad
            print(top_border)

            for line in lines:
                print("│" + space + line  + space + "│")
            print(bottom_border)
        def high_scores(session, player_instance):
            all_high_scores = session.query(HighScore).order_by(HighScore.score.desc()).all()

            grouped_scores = {}
            for high_score in all_high_scores:
                player_id = high_score.player_id
                if player_id not in grouped_scores:
                    grouped_scores[player_id] = []
                grouped_scores[player_id].append(high_score.score)

            top_scores = {}
            for player_id, scores in grouped_scores.items():
                sorted_scores = sorted(scores)[:3]
                top_scores[player_id] = sorted_scores

            players = session.query(Player).filter(Player.id.in_(top_scores.keys())).all()

            for player in players:
                player_scores = ', '.join(map(str, top_scores[player.id]))
                print(f"{player.name}: {player_scores}")
        
        def edit_player(session, player_instance):
            def edit_menu():
                questions = [
                    inquirer.List(
                        "edit_menu",
                        message="Please Select: ",
                        choices=[
                            "Edit Name",
                            "Delete Player",
                            "Go Back"
                        ]
                    )
                ]
                response = inquirer.prompt(questions)
                if response["edit_menu"] == "Edit Name":
                    edit_name(session, player_instance)
                elif response["edit_menu"] == "Delete Player":
                    delete_account(session, player_instance)
                elif response["edit_menu"] == "Go Back":
                    second_menu(session, player_instance)
                else: 
                    print("Invalid Choice")
                    edit_menu()
            edit_menu()

        def edit_name(session, player_instance):
            name = input("Enter New Name: ")
            existing_player = session.query(Player).filter(Player.name == name).first()
            if existing_player:
                print(f"{name} Already Exists. Please Sign In.")
                edit_name(session, player_instance)
            else:
                player_instance.name = name
                session.commit()
                print(f"Player '{name}' has been updated successfully.")
                second_menu(session, player_instance)
        
        def delete_account(session, player_instance):
            print(player_instance)
            confimation = input("Are you sure you want to delete your account? (y/n): ")
            if confimation.lower() == "y":
                session.delete(player_instance)
                session.commit()
                print("Account Deleted Successfully")
                main_menu()
            else:
                print("Action Cancelled")
                second_menu(session, player_instance)
            

        main_menu()
            
if __name__ == "__main__":
    main()

