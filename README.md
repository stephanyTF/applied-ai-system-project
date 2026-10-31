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

## Sample Interactions:

## Design Decisions:

## Testing Summary:

## Reflection:
