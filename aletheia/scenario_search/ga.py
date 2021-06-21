from operator import itemgetter
from random import randint
# from runlocal import evaluate as run_evaluate
import random
from aletheia.settings import BASE_DIR
import json
import os
import shutil
import math


class Gene:
    def __init__(self, **data):
        self.__dict__.update(data)
        self.size = len(data['data'])


class GA:
    def __init__(self, **parameter) -> None:
        '''
        bound: {(start, end): (up, down)}}
        example:
        ga = GA(10, {(1,11):(1,2)}, evaluate_func, result_path, NGEN, CXPB, MUTPB)
        '''
        self.popsize = parameter['popsize']
        self.bound = parameter['bound']
        tmp = {}
        for key, value in self.bound.items():
            if isinstance(key, tuple):
                for i in range(key[0], key[1]):
                    tmp[i] = value
            elif isinstance(key, int):
                tmp[key] = value

        self.bound = tmp
        self.evaluate = parameter['evaluate']
        self.result_path = parameter['result_path']
        self.NGEN = parameter['NGEN']
        self.CXPB = parameter['CXPB']
        self.MUTPB = parameter['MUTPB']
        self.init_the_group()

    def init_the_group(self):
        pop = []
        for i in range(self.popsize):
            geneinfo = [
                randint(self.bound[i][0], self.bound[i][1]) for i in range(len(self.bound))
            ]
            fitness, measure = self.evaluate(geneinfo)
            pop.append({'Gene': Gene(data=geneinfo),
                        'fitness': fitness, 'measure': measure})

        self.pop = pop
        self.bestindividual = self.selectBest(self.pop)

        if os.path.exists(self.result_path):
            if os.path.isfile(self.result_path):
                os.remove(self.result_path)
            elif os.isdir(self.result_path):
                shutil.rmtree(self.result_path)

    def selectBest(self, pop):
        s_inds = sorted(pop, key=itemgetter('fitness'), reverse=True)
        return s_inds[0]

    def selection(self, individuals, k):
        s_inds = sorted(individuals, key=itemgetter('fitness'), reverse=True)
        sum_fits = sum(abs(ind['fitness']) for ind in individuals)
        chosen = []
        for i in range(k):
            u = random.random() * sum_fits
            sum_ = 0
            for ind in s_inds:
                sum_ += abs(ind['fitness'])
                if sum_ >= u:
                    chosen.append(ind)
                    break
        chosen = sorted(chosen, key=itemgetter('fitness'), reverse=True)
        return chosen

    def crossoperate(self, offspring):
        dim = len(offspring[0]['Gene'].data)

        # Gene's data of first offspring chosen from the selected pop
        geninfo1 = offspring[0]['Gene'].data
        # Gene's data of second offspring chosen from the selected pop
        geninfo2 = offspring[1]['Gene'].data

        if dim == 1:
            pos1 = 1
            pos2 = 1
        else:
            # select a position in the range from 0 to dim-1,
            pos1 = random.randrange(1, dim)
            pos2 = random.randrange(1, dim)

        newoff1 = Gene(data=[])  # offspring1 produced by cross operation
        newoff2 = Gene(data=[])  # offspring2 produced by cross operation
        temp1 = []
        temp2 = []
        for i in range(dim):
            if min(pos1, pos2) <= i < max(pos1, pos2):
                temp2.append(geninfo2[i])
                temp1.append(geninfo1[i])
            else:
                temp2.append(geninfo1[i])
                temp1.append(geninfo2[i])
        newoff1.data = temp1
        newoff2.data = temp2

        return newoff1, newoff2

    def mutation(self, crossoff, bound):
        dim = len(crossoff.data)
        if dim == 1:
            pos = 0
        else:
            pos = random.randrange(0, dim)
        crossoff.data[pos] = random.randint(bound[pos][0], bound[pos][1])
        return crossoff

    def save_gen(self, gen):
        with open(self.result_path, 'a', encoding='utf-8') as f:
            datas = {
                'gen': gen,
                # 'pop': [data.]
                'pop': [
                    {'Gene': x['Gene'].data, 'fitness': x['fitness'], 'measure':x['measure']} for x in self.pop
                ],
                'best': {'Gene': self.bestindividual['Gene'].data, 'fitness': self.bestindividual['fitness'], 'measure': self.bestindividual['measure']}
            }
            datas = json.dumps(datas, ensure_ascii=False)
            f.write(datas + "\n")

    def GA_main(self):
        popsize = self.popsize
        print('Start of evolution')
        NGEN = self.NGEN
        CXPB = self.CXPB
        MUTPB = self.MUTPB

        for g in range(NGEN):
            print('############ Generation {} ############'.format(g))
            self.save_gen(g)

            selectpop = self.selection(self.pop, popsize)

            nextoff = []
            while len(nextoff) != popsize:
                if len(selectpop) < 2:
                    print('debug')
                offspring = [selectpop.pop() for _ in range(2)]

                if random.random() < CXPB:
                    crossoff1, crossoff2 = self.crossoperate(offspring)
                    if random.random() < MUTPB:  # mutate an individual with probability MUTPB
                        muteoff1 = self.mutation(crossoff1, self.bound)
                        muteoff2 = self.mutation(crossoff2, self.bound)
                        # Evaluate the individuals
                        fit_muteoff1, measure = self.evaluate(
                            muteoff1.data)
                        # Evaluate the individuals
                        fit_muteoff2, measure = self.evaluate(
                            muteoff2.data)
                        nextoff.append(
                            {'Gene': muteoff1, 'fitness': fit_muteoff1, 'measure': measure})
                        nextoff.append(
                            {'Gene': muteoff2, 'fitness': fit_muteoff2, 'measure': measure})
                    else:
                        fit_crossoff1, measure = self.evaluate(
                            crossoff1.data)  # Evaluate the individuals
                        fit_crossoff2, measure = self.evaluate(
                            crossoff2.data)
                        nextoff.append(
                            {'Gene': crossoff1, 'fitness': fit_crossoff1, 'measure': measure})
                        nextoff.append(
                            {'Gene': crossoff2, 'fitness': fit_crossoff2, 'measure': measure})
                else:
                    nextoff.extend(offspring)

            self.pop = nextoff
            fits = [ind['fitness'] for ind in self.pop]

            best_ind = self.selectBest(self.pop)

            if best_ind['fitness'] > self.bestindividual['fitness']:
                self.bestindividual = best_ind

            print("Best individual found is {}, {}".format(self.bestindividual['Gene'].data,
                                                           self.bestindividual['fitness']))
            print("  Max fitness of current pop: {}".format(max(fits)))


if __name__ == '__main__':
    CXPB, MUTPB, NGEN, popsize = 0.8, 0.4, 1000, 100  # popsize must be even number
    parameter = [CXPB, MUTPB, NGEN, popsize]
    run = GA(agent_number=116, popsize=1000)
    # run.GA_main()
    run.GA_draw(skip=False, sort=True)
