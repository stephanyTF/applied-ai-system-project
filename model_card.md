# Limitations / Biases
**Limitations**: 
    - Suggests 3 PetCare Tasks even if the task descriptions are not relevant to the pet
    - User can't change the suggested task's start time, duration, or priority
    - Manual drop the cards one by one else they will persist in the next session
    
**Bias**
- The suggested tasks fit well only for more well known animals like cats or dogs but may not reflect the needs well on more obscure pets like a "Degus"

# Potential AI Misuses and Preventions
- Bad actors may attempt to put invalid or non relevant and potentially manipulative prompts in the species entry box (since it allows free writes)
- Possible prevention is more guardrails that checks the input before sending it to the llm to ensure it's fits the critiera (one word, maybe matches a list of known animals)

# Surprises During AI's test reliability
- When I was manually testing the task suggestion and put in a non animal input for the species box, I was surprised to see it try to generate tasks related to it even though it didn't make any sense. Example for an input like "Fashionista", it generated tasks like "Grooming" or "Playing" and these tasks can be exclusive to other species so it makes me think what animal the llm was associating the invalid species term to. 


# Claude CoWork

**What Worked Well**: Claude gives great feedback on my plans and helping expand it. It helps reorganizes my thoughts and can tailor to my vision through back and forth discussion. 

**Where I Stepped In**: Despite Claude's generated test file for the new ai suggester feature, the test passed with flying colors. I had to step in to test the site manually and found several bugs that Claude missed. This was an good habit of double checking an LLM's work since it may be biased to test on what it knows vs anticipate how users may use it differently. 
