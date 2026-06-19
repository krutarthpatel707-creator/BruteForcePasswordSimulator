import itertools
import string
import time


def brute_force_attack(target_password, update_callback=None):

    characters = string.ascii_lowercase

    attempts = 0
    start_time = time.time()

    for length in range(1, len(target_password) + 1):

        for guess in itertools.product(characters, repeat=length):

            attempts += 1

            guessed_password = ''.join(guess)

            if attempts % 1000 == 0 and update_callback:
                update_callback(attempts)

            if guessed_password == target_password:

                end_time = time.time()

                return {
                    "password": guessed_password,
                    "attempts": attempts,
                    "time": round(end_time - start_time, 4)
                }

    return None