# 🌍 PyKWorldSim

> A lightweight Python simulation engine for modeling **people, relationships, cities, and dynamic worlds**.

PyKWorldSim provides a modular framework to simulate interactions between entities such as individuals, locations, jobs, and events — making it useful for experiments in **AI, social simulations, and system modeling**.

---

## 🚀 Features

- 👤 **Person system** — create and manage individuals  
- 🤝 **Relationships** — model connections between people  
- 🏙️ **Locations & cities** — simulate environments  
- 💼 **Jobs & roles** — assign occupations  
- 🎯 **Goals** — define motivations and behaviors  
- 📅 **Events** — simulate time-based interactions  
- 📊 **Reports** — analyze simulation outcomes  

---

## 📦 Installation

### From PyPI (after publishing)

```bash
pip install pykworldsim
```

### For local development

```bash
pip install .
```

---

## 🧠 Basic Usage

```python
from pykworldsim.world import World
from pykworldsim.person import Person

# Create world
world = World()

# Create people
alice = Person(Name="Alice")
bob = Person(Name="Bob")

# Add people to the world
world.addPerson(alice)
world.addPerson(bob)

# Run simulation step (example)
world.Simulate()

# Generate report
report = world.generate_report()
print(report)
```

---

## 📁 Project Structure

```
pykworldsim/
│
├── pykworldsim/
│   ├── world.py
│   ├── person.py
│   ├── relationship.py
│   ├── goal.py
│   ├── event.py
│   ├── job.py
│   ├── location.py
│   └── report.py
│
├── pyproject.toml
├── README.md
└── LICENSE
```

---

## ⚙️ Requirements

- Python 3.8+

---


## 📌 Use Cases

- AI simulations  
- Social behavior modeling  
- Game prototyping  
- Agent-based systems  
- Experimental world-building  

---

## 📜 License

This project is licensed under the MIT License.

---

## 👤 Author

**Kairav Dutta**

---

## ⭐ Contributing

Contributions, issues, and feature requests are welcome and appreciated!
