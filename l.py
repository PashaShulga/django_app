

class Question(object):

    def quest(self):
        with open('questions.txt', 'r') as file:
            i = file.readlines()
            try:
                i_len = 0
                while True:
                    magic = int(input("%s = " % (i[i_len].split('\n')[0],)))
                    if magic is eval(i[i_len]):
                        print('Right!')
                        i_len += 1
                        if i_len == len(i):
                            break
                    else:
                        print('Try again: ')
            except Exception as e:
                print("Error: ", e)


if __name__ == '__main__':
    Question().quest()