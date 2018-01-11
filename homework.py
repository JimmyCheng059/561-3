import itertools
import copy


class Clause:
    def __init__(self, func, obj):
        self.function = func
        self.objects = obj


class Sentence:
    def __init__(self, lit):
        self.list = lit


def parser(filename):
    files = open(filename, 'r').readlines()
    index = 0
    qpointer = 0
    kbpointer = 0
    querylist = list()
    kb = list()
    for line in files:
        if index == 0:
            qpointer = int(line)
        elif index <= qpointer:
            tmp = list()
            clauselist = line.rstrip().replace(" ", "").split("|")
            for x in clauselist:
                tmp.append(string_to_clause(x))
            querylist.append(Sentence(tmp))
        elif index == qpointer + 1:
            kbpointer = int(line)
        elif index <= kbpointer + qpointer + 1:
            tmp = list()
            clauselist = line.rstrip().replace(" ", "").split("|")
            for x in clauselist:
                tmp.append(string_to_clause(x))
            kb.append(Sentence(tmp))
        index += 1
    return querylist, kb


def target(clause):
    if clause.function[0] is "~":
        return clause.function.replace("~", "")
    else:
        return "~" + clause.function


def string_to_clause(str):
    cla = Clause(0, 0)
    cla.function = str.split("(")[0]
    cla.objects = str.split("(")[1].replace(")", "").split(",")
    return cla


def normalize(kb):
    index = 0
    for sentence in kb:
        seen = {}
        for x in sentence.list:
            for y in range(0, len(x.objects)):
                if x.objects[y][0].islower() and x.objects[y] not in seen:
                    newy = "v" + str(len(seen)) + "s" + str(index)
                    seen[x.objects[y]] = newy
                    x.objects[y] = newy
                if x.objects[y][0].islower() and x.objects[y] in seen:
                    x.objects[y] = seen[x.objects[y]]
        index += 1


def unify(clause, sentence):
    tgtlist = list()
    for opt in clause.list:
        tgt = target(opt)
        tgtlist.append(tgt)
    index2 = -1
    for cla in sentence.list:
        index2 += 1
        if cla.function in tgtlist:
            index = tgtlist.index(cla.function)
            dictclause = {}
            dictcla = {}
            for i in range(0, len(cla.objects)):
                if cla.objects[i][0].isupper() and clause.list[index].objects[i][0].isupper():
                    if cla.objects[i] != clause.list[index].objects[i]:
                        return 2
                elif cla.objects[i][0].isupper() and clause.list[index].objects[i][0].islower():
                    if clause.list[index].objects[i] in dictclause:
                        if dictclause[clause.list[index].objects[i]] != cla.objects[i]:
                            return 2
                    else:
                        dictclause[clause.list[index].objects[i]] = cla.objects[i]
                elif clause.list[index].objects[i][0].isupper() and cla.objects[i][0].islower():
                    if cla.objects[i] in dictcla:
                        if dictcla[cla.objects[i]] != clause.list[index].objects[i]:
                            return 2
                    else:
                        dictcla[cla.objects[i]] = clause.list[index].objects[i]
                elif clause.list[index].objects[i][0].islower() and cla.objects[i][0].islower():
                    return 2
            tmpclause = copy.deepcopy(clause)
            tmpsentence = copy.deepcopy(sentence)
            tmpclause.list.remove(tmpclause.list[index])
            tmpsentence.list.remove(tmpsentence.list[index2])
            if len(tmpclause.list) + len(tmpsentence.list) < 1:
                return 1
            for x in tmpclause.list:
                for i in range(0, len(x.objects)):
                    if x.objects[i] in dictclause:
                        x.objects[i] = dictclause[x.objects[i]]
            for x in tmpsentence.list:
                for i in range(0, len(x.objects)):
                    if x.objects[i] in dictcla:
                        x.objects[i] = dictcla[x.objects[i]]
            newlist = tmpsentence.list + tmpclause.list
            return Sentence(newlist)
    return 2


def is_same(sentence1, sentence2):
    if len(sentence1.list) < len(sentence2.list):
        return False
    elif len(sentence1.list) > len(sentence2.list):
        for subsen in itertools.combinations(sentence1.list, len(sentence2.list)):
            tmp = Sentence(subsen)
            check = is_same(tmp, sentence2)
            if check:
                return True
    elif len(sentence1.list) == len(sentence2.list):
        tgt = list()
        tgt2 = list()
        for x in sentence1.list:
            tgt.append(x.function)
        for y in sentence2.list:
            tgt2.append(y.function)
        if set(tgt) != set(tgt2):
            return False
        s1dict = {}
        s2dict = {}
        alllist = list()
        for s1 in sentence1.list:
            sublist = list()
            for s2 in sentence2.list:
                flag = True
                if s1.function != s2.function:
                    flag = False
                else:
                    for i in range(0, len(s1.objects)):
                        if s1.objects[i][0].isupper() and s2.objects[i][0].isupper():
                            if s1.objects[i] != s2.objects[i]:
                                flag = False
                        elif s1.objects[i][0].isupper() and s2.objects[i][0].islower():
                            flag = False
                        elif s1.objects[i][0].islower() and s2.objects[i][0].isupper():
                            flag = False
                        elif s1.objects[i][0].islower() and s2.objects[i][0].islower():
                            if s1.objects[i] in s1dict:
                                if s1dict[s1.objects[i]] != s2.objects[i]:
                                    flag = False
                            elif s2.objects[i] in s2dict:
                                if s2dict[s2.objects[i]] != s1.objects[i]:
                                    flag = False
                            else:
                                s1dict[s1.objects[i]] = s2.objects[i]
                                s2dict[s2.objects[i]] = s1.objects[i]
                sublist.append(flag)
            if True not in sublist:
                return False
            alllist.append(sublist)
        for lit in itertools.permutations(alllist, len(sentence1.list)):
            check = True
            for i in range(0, len(sentence1.list)):
                if not lit[i][i]:
                    check = False
            if check:
                return True
    return False


def resolution(kb):
    normalize(kb)
    new = list()
    for x in itertools.combinations(kb, 2):
        a = unify(x[0], x[1])
        if a == 2:
            continue
        elif a == 1:
            return True
        else:
            flag = False
            for sen in kb:
                if is_same(a, sen):
                    flag = True
                    break
            if not flag:
                new.append(a)
    if len(new) < 1:
        return False
    kab = kb + new
    return resolution(kab)


def reverse(sentence):
    for x in sentence.list:
        if x.function[0] == "~":
            x.function = x.function.replace("~", "")
        else:
            x.function = "~" + x.function


init = parser("input.txt")

for q in init[0]:
    reverse(q)

file_output = open("output.txt", 'w')

for query in init[0]:
    init[1].append(query)
    result = resolution(init[1])
    if result:
        file_output.write("TRUE")
    else:
        file_output.write("FALSE")
    file_output.write("\n")
    del init[1][-1]
