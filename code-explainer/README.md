# 🧩 Code Explainer

**AI-Powered Code Translation & Documentation Generator**

Transform complex code into plain English explanations, automatically generate documentation, and help understand unfamiliar programming concepts.

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-FF4B4B?logo=streamlit)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT-412991?logo=openai)

---

## 🎯 Overview

Code Explainer uses OpenAI GPT to break down code into understandable explanations, generate comprehensive documentation, and translate logic into plain English. Perfect for code reviews, learning new languages, or documenting legacy code.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| **Plain English Translation** | Explain code logic in simple, non-technical terms |
| **Auto Documentation** | Generate docstrings and comments automatically |
| **Function Summaries** - Get high-level overviews of what functions do |
| **Line-by-Line Breakdown** - Detailed explanation of each code section |
| **Code Explanation** - Explain why code is written this way |
| **Multi-Language Support** - Understand Python, JavaScript, Java, C++, and more |
| **Best Practices Suggestions** - Get tips for code improvement |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11 or higher
- OpenAI API key

### Installation

```bash
# Clone the repository
git clone https://github.com/guiltyfalcon/ai-portfolio.git
cd ai-portfolio/code-explainer

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Create a `.streamlit/secrets.toml` file with your OpenAI API key:

```toml
OPENAI_API_KEY = "sk-your-api-key-here"
```

Get your API key at [platform.openai.com](https://platform.openai.com)

### Running the App

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

---

## 📊 How It Works

### Analysis Process

1. **Code Input** - Paste or upload your code snippet
2. **Language Detection** - Automatically identifies programming language
3. **Structure Parsing** - Identifies functions, classes, and logic flow
4. **GPT Analysis** - OpenAI GPT generates explanations and documentation
5. **Formatted Output** - Display explanations with syntax highlighting

### Explanation Types

- **Executive Summary** - High-level overview in plain English
- **Function Documentation** - Docstrings following standard formats
- **Logic Flow** - Step-by-step explanation of how code works
- **Purpose** - Why this code exists and what problem it solves

---

## 🏗️ Architecture

```
code-explainer/
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
└── .streamlit/
    └── secrets.toml           # API keys (create this)
```

---

## 💬 Example Usage

### Input Code
```python
def quicksort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quicksort(left) + middle + quicksort(right)
```

### Output Explanation
**Plain English:**
> This function sorts a list of numbers using the quicksort algorithm. It picks a middle number as a "pivot," then splits the list into three groups: numbers smaller than the pivot, equal to it, and larger than it. It then recursively sorts the smaller and larger groups, and finally combines everything back together in sorted order.

---

## 💡 Use Cases

| Use Case | Example |
|----------|---------|
| **Code Reviews** - Explain PR code to reviewers |
| **Onboarding** - Help new team members understand codebase |
| **Learning** - Study code in unfamiliar languages |
| **Documentation** - Auto-generate docs for legacy code |
| **Debugging** - Understand what code is supposed to do |
| **Teaching** - Create educational materials from code |

---

## ⚙️ Configuration Options

### Explanation Detail Level

Edit `app.py` to adjust detail:

```python
detail_level = "medium"  # "simple", "medium", or "detailed"
```

### Documentation Style

Choose your preferred docstring format:

```python
docstyle = "google"  # "google", "numpy", or "sphinx"
```

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| "API key not found" | Add OPENAI_API_KEY to secrets.toml |
| Explanation too long | Reduce code snippet size |
| Poor quality explanations | Provide more context with your question |
| Language not recognized | Specify language in comments |

---

## 🔮 Future Enhancements

- [ ] File upload for entire codebase analysis
- [ ] Code translation between languages
- [ ] Security vulnerability detection
- [ ] Performance optimization suggestions
- [ ] Generate unit tests from code
- [ ] UML diagram generation
- [ ] Integration with GitHub/GitLab

---

## 💰 Cost Estimate

Using GPT-3.5-turbo:
- ~$0.001-0.005 per code snippet
- 100 explanations ≈ $0.10-0.50

Very affordable for code documentation!

---

## 📝 License

MIT License — Feel free to use and modify.

---

## 🙏 Credits

- **OpenAI** - GPT code analysis
- **Streamlit** - Web application framework
- **Pygments** - Syntax highlighting

---

Part of the [AI Portfolio](../) collection.