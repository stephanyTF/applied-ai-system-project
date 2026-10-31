# Applied AI System: PawPal+ w/ Tailored PetCare Tasks Suggester (Unit 8)


## Summary
The PawPal+ is a smart, AI-enhanced pet task scheduler that can automatically suggest relevant tasks for pets to make it faster and easier for pet owners in planning their pet care schedule. 


## Architecture Overview: @architecture.mmd

1. Input:
    A user first adds a pet and enters its name and species (i.e.: cat, dog, etc) to be passed on to the PetCareTask Suggester

2. Proccess:
    Based on the given pet information, Gemini LLM is called to create 3 PetCareTasks that's tailored and relevant to the pet like "Walking <Dog's name>" or "Scooping <cat's name> Litter Box". 


3. Validation 
    Before displaying to the user, each of the tasks are checked to ensure their title cards are relevant and altogether meets the required amount. 
    
4. Output

    3 PetCare tasks are outputed with a relevant title, task time start, time duration, priority, and 3 selectable options ("Accept", "Edit", "Drop")

5. User's Intervention
    The user has the choice of accepting, editing or dropping the task. If accepted or edited, the task will be added to the current task list (session_state.tasks) or otherwise discarded. 

## Setup Instructions:

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Running
- Open the terminal and write ``streamlit run app.py``
- Run tests: ``pytest test_suggester.py -v``

## Sample Interactions:

Case #1:
User, Kiki, adds in their pet cat "Jiji" and gets 3 automatically suggested pet care tasks for him. Kiki accepts the first task "Feed Jiji" while Kiki modifies the time duration of the second task, "Brush Jiji". The last task Kiki rejects because it doesn't apply to Jiji's case.

Case #2
User, Katie, adds in her two dogs, Max and Duke. Given 3 suggested tasks, she reads through the first set of task for Max (accepting and modifying a few) before moving to the tasks generated for Duke. She accepts all three and adds her accepted task into her schedule.

## Design Decisions:
**Why AI-suggested tasks:** Suggestions make it faster to build a schedule without entering every task manually. Users can accept a task instantly, edit it, or drop it, so they stay in control.

**Why an LLM instead of a fixed template:** A static species-to-tasks list would be faster and free, but an LLM tailors tasks to the pet's name and species (e.g., "Scooping Jiji's Litter Box").

**Trade-offs**:
- Irrelevant suggestions cost the user time to discard. The validation step reduces this but can't eliminate it.
- Depends on the Gemini API, so there is added latency, possible rate limits and a required API key.
- Output can vary between runs for the same pet.

## Testing Summary:
12/12 test case passed from test_suggester.py

3/6 passed Human Eval Test of the Website

**Missed from Human Eval:**
- Robustness: Suppose to only show the suggested task related to the recently added pet however FAILs because it's not set to clear our suggested task (dependent on the user to drop them manually)
- Times still overlap (not considering duration)
- Bad Species Input case test:
    When the species was a non animal like "Fashionista", it still gave out 3 tasks that were not relevant at all to the species

**What could be improved:**
- More robust design: In the case a user doesn't discard the suggested task, when they add a new pet, the previous suggested tasks still persist which clutters the UI.

- Prevent overlapping scheduling by taking "duration" into consideration

- Don't pass invalid species input (non animal, wrong data type) or the animal is not widely known to generate common pet care tasks


## Reflection:
Claude is a great collaborative coding tool where you can share plans, quickly implement them into working features, and test. However, it's always best to critically think through Claude outputs to make significant decisions or catch needed improvements.  
