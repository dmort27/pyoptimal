#!/usr/bin/env python3
"""
Compare different OT learning algorithms on the same dataset.
"""

from pyoptimal import Grammar, Learner
from pyoptimal.ot import GLALearner, MaxEntLearner

def main():
    # Load a simple OT grammar
    grammar = Grammar.from_yaml("simple_ot.yaml")
    
    print("="*60)
    print("Comparing OT Learning Algorithms")
    print("="*60)
    print(f"\nGrammar: {len(grammar.constraints)} constraints, {len(grammar.examples)} examples")
    print(f"Constraints: {', '.join(c.name for c in grammar.constraints)}")
    print()
    
    # Test each algorithm
    algorithms = ["ot", "rcd", "edcd", "gla", "maxent"]
    
    for algo in algorithms:
        print(f"\n{algo.upper():=^60}")
        
        learner = Learner(grammar, algorithm=algo)
        ranking = learner.train()
        
        print(f"Ranking: {ranking}")
        
        # Show additional information for GLA and MaxEnt
        if algo == "gla":
            gla = GLALearner(grammar)
            gla.learn()
            values = gla.get_ranking_values()
            print("\nRanking values:")
            for name in sorted(values.keys(), key=lambda k: values[k], reverse=True):
                print(f"  {name}: {values[name]:.2f}")
        
        elif algo == "maxent":
            maxent = MaxEntLearner(grammar)
            maxent.learn()
            weights = maxent.get_weights()
            print("\nWeights:")
            for name in sorted(weights.keys(), key=lambda k: weights[k], reverse=True):
                print(f"  {name}: {weights[name]:.4f}")
    
    print("\n" + "="*60)
    print("Comparison complete!")
    print("="*60)

if __name__ == "__main__":
    main()
