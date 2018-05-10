# -*- coding: utf-8 -*-

from igraph import *
from utils import *
from gltl2gpar import drawGPar,sequencer_rmg_single,sequencer_cgs_single
from generatepun import compute_pun
import time

def nonemptiness(modules,GPar,draw_flag,cgsFlag):
    TTPG_vmax=0 #count the max number of vertices in TTPG/GPar sequentialisation
    TTPG_emax=0 #count the max number of edges in TTPG/GPar sequentialisation
    TTPG = Graph(directed=True) #init GPar sequentialisation
    perfPGSolver = 0.0

    '''
    generate W (winning coalitions)
    reverse the list to generate from big to small
    hence always gets pareto optimal if NE exists    
    '''
    W = list(reversed(generate_set_W(modules)))
    '''Compute G^{-L}_{PAR}'''
    GPar_L = Graph(directed=True)
    NE_flag=False
    PUN = {}
    for w in W:
        if len(w)==len(modules):
            '''trivial cases all win/lose'''
            s_Alpha = build_streett_prod(GPar,w,modules)
            L,L_sigma = Streett_emptyness(GPar,s_Alpha,modules)
            '''if not empty'''
            if L.vcount()!=0:
                print '>>> YES, there exists NE <<<'
                print 'Winning Coalition',(num2name(w,modules))
                NE_flag=True
                if draw_flag:
                    '''draw & printout strategy progile \vec{sigma}'''
                    drawGPar(L_sigma)
                    printGParDetails(L_sigma)
                break
        else:
            l = get_l(list(w),modules)
            PUN_L = set([v.index for v in GPar.vs])
            for pl in l:
                pl_name = list(modules[pl][1])[0]
                try:
                    if TTPG[pl_name]:
                        pass
                except KeyError:
                    print "\n Sequentialising GPar for punishing <"+pl_name+">"
                    if not cgsFlag:
                        startPGSolver = time.time()*1000
                        sequencer_rmg_single(pl,GPar,TTPG,modules)
                        perfPGSolver = perfPGSolver + time.time()*1000 - startPGSolver
                        if TTPG_vmax<TTPG[pl_name].vcount():
                            TTPG_vmax=TTPG[pl_name].vcount()
                        if TTPG_emax<TTPG[pl_name].ecount():
                            TTPG_emax=TTPG[pl_name].ecount()
                    else:
                        startPGSolver = time.time()*1000
                        sequencer_cgs_single(pl,GPar,TTPG,modules)
                        perfPGSolver = perfPGSolver + time.time()*1000 - startPGSolver
                        if TTPG_vmax<TTPG[pl_name].vcount():
                            TTPG_vmax=TTPG[pl_name].vcount()
                        if TTPG_emax<TTPG[pl_name].ecount():
                            TTPG_emax=TTPG[pl_name].ecount()
                            
                '''compute pl_name pun region'''
                if pl_name not in PUN:
                    print "\n Computing punishing region for <"+pl_name+">"
                    PUN=compute_pun(pl_name,PUN,TTPG)
                PUN_L = PUN_L.intersection(set(PUN[pl_name]))
                '''init state s0 not included in PUN_L'''
                if 0 in PUN_L:        
                    GPar_L[frozenset(l)]=build_GPar_L(GPar,w,l,PUN_L)
                else:
                    GPar_L[frozenset(l)]=Graph(directed=True)

            if GPar_L[frozenset(l)].vcount()!=0:
                '''build the product of streett automata'''
                s_Alpha = build_streett_prod(GPar_L[frozenset(l)],w,modules)
                '''check street automaton emptiness'''
                L,L_sigma = Streett_emptyness(GPar_L[frozenset(l)],s_Alpha,modules)

                '''if not empty'''
                if L.vcount()!=0:    
                    print '>>> YES, there exists NE <<<'
                    print 'Winning Coalition',num2name(w,modules)
                    if draw_flag:
                        '''draw & printout strategy progile \vec{sigma}'''
                        drawGPar(L_sigma)
                        printGParDetails(L_sigma)
                    NE_flag=True
                    break
                
    if not NE_flag:
        print '>>> NO, there exists no NE <<<'
    return perfPGSolver,TTPG_vmax,TTPG_emax