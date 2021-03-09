from RaiseWikibase.dbconnection import DBConnection
from RaiseWikibase.datamodel import label, alias, description, snak, claim, entity
from RaiseWikibase.raiser import batch
import random
import string
import time
import pandas as pd
import seaborn as sns


def item_claim(nc=1, extra=0):
    s = ''.join(random.choice(letters) for i in range(30))
    if extra == 0:
        q, r = [], []
    if extra == 1:
        q, r = [snak('string', s, 'P1')], []
    if extra == 2:
        q, r = [snak('string', s, 'P1')], [snak('string', s, 'P1')]
    edict = entity(labels={'en': {'language': 'en', 'value': s}},
                   aliases={'en': [{'language': 'en', 'value': s}]},
                   descriptions={'en': {'language': 'en', 'value': s}},
                   claims=claim('P1',
                                snak('string', s, 'P1'),
                                qualifiers=q,
                                references=r),
                   etype="item",
                   datatype='string')
    if nc >= 2:
        for n in range(2, nc + 1):
            edict['claims'].update(claim('P' + str(n),
                                         snak('string', s, 'P' + str(n)),
                                         qualifiers=q,
                                         references=r))
    return edict


if __name__ == "__main__":
    time1 = time.time()
    batch_lengths = [100] # a list of batch lenghts used in experiments; 
    # the length of batch 10000 makes it time consuming;
    # start with 100, then running both experiments takes 80 seconds
    dir_experiments = './experiments/'
    connection = DBConnection()
    ## Experiment 1
    letters = string.ascii_lowercase
    res = []
    for k in [1, 2, 3, 4, 5, 6]:  # number of a test
        for nc in [500, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000, 5500, 6000]:  # length of a page
            t = ''.join(random.choice(letters) for i in range(nc))
            for nn in batch_lengths:  # length of the batch
                time0 = time.time()
                batch('wikitext', [t for m in range(nn)], 0, [str(random.random()) for m in range(nn)])
                nt = time.time() - time0
                res.append([nc, nn, nt, k])
    d = pd.DataFrame(res, columns=['Number of characters per page', 'Number of pages', 'Time, [s]', 'Run'])
    d['Speed in pages per second'] = d['Number of pages'] / d['Time, [s]']
    # Save data
    d.to_csv(dir_experiments + 'exp1.csv')
    # Plot data and save the figure
    sns.set_theme(style="darkgrid")
    sns.set_context("paper", font_scale=1.5, rc={"font.size": 15, "axes.titlesize": 15, "axes.labelsize": 15})
    ax = sns.scatterplot(data=d, y="Speed in pages per second", x="Number of characters per page", hue="Run",
                         style="Run", s=180, legend=False)
    ax.figure.savefig(dir_experiments + 'exp1.pdf', dpi=300, bbox_inches='tight')

    # Experiment 2
    letters = string.ascii_lowercase
    res = []  # [['nc','nn','nt']]
    for e in [0, 1, 2]:  # 0 - each claim with no qualifiers and no references,
        # 1 - each claim with one qualifer and no reference,
        # 2 - each claim with one qualifer and one reference.
        for k in [1, 2]:  # number of a test
            for nc in [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21]:  # number of claims per item
                for nn in batch_lengths:  # length of the batch
                    it = item_claim(nc, e)
                    time0 = time.time()
                    batch('wikibase-item', [it for m in range(nn)])
                    nt = time.time() - time0
                    res.append([nc, nn, nt, k, e])
    d = pd.DataFrame(res, columns=['Number of claims per page', 'Number of pages', 'Time, [s]', 'Run', 'Extra'])
    d['Speed in pages per second'] = d['Number of pages'] / d['Time, [s]']
    # Save data
    d.to_csv(dir_experiments + 'exp2.csv')
    # Plot data and save the figure
    sns.set_theme(style="darkgrid")
    sns.set_context("paper", font_scale=1.5, rc={"font.size": 15, "axes.titlesize": 15, "axes.labelsize": 15})
    ax = sns.scatterplot(data=d, y="Speed in pages per second", x="Number of claims per page", hue="Run", style="Extra",
                         s=180, legend=False)
    ax.figure.savefig(dir_experiments + 'exp2.pdf', dpi=300, bbox_inches='tight')

    print(time.time()-time1)