# 🍽️ Understanding Testing — In the Language of Sahyog Restaurant

> *"Writing code is a job. Testing it properly is a different skill altogether."*

---

## 🏠 Let's First Meet — Sahyog Restaurant

Imagine a popular restaurant, **Sahyog Restaurant** — on FC Road, Pune. From morning till night, the aroma of Biryani, Dal Makhani, Butter Naan, and Masala Chai fills the air.

The main people at the restaurant are:

| Role | Name | Job |
|---|---|---|
| 👨‍🍳 Head Chef | **Raju Bhai** | Prepares all the food. |
| 🧑‍💼 Manager | **Ramesh Bhai** | Runs the restaurant and classifies orders. |
| 🙋 Waiter | **Suresh** | Takes orders from the customers. |
| 📋 Expediter | **Vinod** | Delivers orders to the kitchen and compresses noise. |
| 🧑‍⚖️ Food Inspector | **Sharma Ji** | Checks if everything is correct or not. |

Now, we will understand **automated testing** through these people. 🎯

---

## 🧑‍⚖️ Who is Sharma Ji? (What is pytest?)

**Sharma Ji** is the Government **Food Safety Inspector**. Every month, he visits Sahyog Restaurant with a **checklist** and audits the entire restaurant.

```text
Sharma Ji's Checklist:
✅ Did the chef wash his hands?
✅ Is the Biryani temperature correct?
✅ Does the Dal Makhani have the right amount of salt?
✅ Was the tea served properly?
✅ Was the order billing correct?
```

This checklist is your **test suite**.
And Sharma Ji himself is **pytest** — who runs all the checks.

> 💡 **In Python:** `pytest tests/ -v` = Sharma Ji's full inspection

---

## 📋 Each Check = Each Test Function

**Each item** on Sharma Ji's checklist is a **test function**:

```python
def test_biryani_temperature_is_correct():
    """Biryani must be served above 70 degrees."""
    temperature = kitchen.get_biryani_temperature()
    assert temperature >= 70  # ✅ PASS or ❌ FAIL
```

If the Biryani turns out to be cold — `FAILED` ❌
If it comes out at the correct temperature — `PASSED` ✅

This is exactly what happens when you write:
```python
def test_enhance_returns_200_with_valid_prompt(client):
    response = client.post("/v1/enhance", json={"prompt": "fix my code"})
    assert response.status_code == 200  # Was the response correct?
```

---

## 🥘 Real Ingredients vs Fake Ingredients (Mocking)

Now, here is a **very important concept**. 🌟

When Sharma Ji comes for an inspection, he **does not make actual Biryani**. Why? Because:

- 🕐 Making real Biryani takes 2 hours (very slow)
- 💰 Real ingredients cost money (very expensive)
- 🌡️ Every time, the Biryani might be slightly different (non-deterministic)

So what does Sharma Ji do? He uses **fake dummy ingredients** — just to test the process.

> 💡 **This is MOCKING!**

We do not make an actual call to the Gemini API in our tests. We create a **fake Gemini** that responds instantly:

```python
# ❌ Wrong — Will make a Real Gemini call (slow, expensive, unpredictable)
response = client.post("/v1/enhance", json={"prompt": "fix my code"})

# ✅ Correct — Use Fake Gemini (fast, free, predictable)
fake_response = '{"enhanced_prompt": "Debugged code...", "reasoning": "Fixed the error"}'

with patch("app.services.enhancer.llm_provider.generate",
           new=AsyncMock(return_value=fake_response)):
    response = client.post("/v1/enhance", json={"prompt": "fix my code"})
```

### 🍛 Restaurant Example:

```text
Real World:
Sharma Ji → "Raju Bhai, make Biryani" → Raju Bhai works for 2 hours → Taste test

With Mocking:
Sharma Ji → Brings a "ready-made dummy Biryani" himself → Only checks the process
             ↑ this is AsyncMock(return_value="fake_biryani")
```

---

## 🧰 Sharma Ji's Toolkit (conftest.py + fixtures)

When Sharma Ji comes for an inspection, he carries a **black bag**. Inside it is:

- 🌡️ Thermometer (for temperature checks)
- ⚖️ Weighing scale (for portion checks)
- 📋 Standard checklist
- 🔦 Torch (to check dark corners)

This bag is **the same for every inspection** — he doesn't buy a new one every time.

> 💡 **This is `conftest.py`** — a shared toolkit that every test file can automatically use.

```python
# conftest.py — Sharma Ji's toolkit
@pytest.fixture
def client():
    """
    This is a fake HTTP connection to Syntra.
    Every test can automatically use this.
    """
    with TestClient(app) as test_client:
        yield test_client
```

Now, we just add `client` as a parameter in every test — no manual setup needed:

```python
def test_anything(client):  # ← receives client automatically from conftest.py
    response = client.post("/v1/enhance", ...)
```

---

## 🚫 Testing the Wrong Order (Negative Tests / pytest.raises)

Sharma Ji doesn't just check if everything works correctly. He also checks if **incorrect things are rejected properly**.

**Example:**
> A customer arrives and says: "Brother, I want 0 Biryani."
> Sahyog Restaurant's system **rejects** it — negative quantity is not allowed.
> Sharma Ji checks: "Did the system reject it? ✅"

```python
def test_zero_biryani_order_is_rejected():
    """Order of 0 items should be rejected."""
    with pytest.raises(ValidationError):  # ← We EXPECT an error to happen
        BiryaniOrder(quantity=0)  # This should fail!
```

```python
# In Syntra, it looks like this:
def test_enhance_rejects_empty_prompt(client):
    """Empty prompt should be rejected — Pydantic will catch it."""
    response = client.post("/v1/enhance", json={"prompt": ""})
    assert response.status_code == 422  # ← Rejection is expected!
```

---

## 🍽️ Unit Test vs Integration Test

### 🥘 Unit Test — Just check the Dal
Sharma Ji is only checking the **Dal Makhani recipe** — in isolation. No Naan, no Biryani. Just Dal.

```python
# Unit Test — test only one thing
def test_routing_request_optional_fields():
    req = RoutingRequest(prompt="Help me debug")
    assert req.code_context is None  # Is the optional field None?
    assert req.language is None      # No HTTP, no LLM
```

⚡ **Very fast** — runs in milliseconds

### 🍱 Integration Test — Test the Full Thali
Now Sharma Ji is testing a full **thali order** — the customer placed an order, the kitchen prepared it, the waiter served it — all at once.

```python
# Integration Test — test the full flow
def test_enhance_returns_200_with_valid_prompt(client):
    # Set up Fake Gemini
    with patch("...llm_provider.generate", new=AsyncMock(return_value=fake_json)):
        # Send HTTP request (like a real customer would)
        response = client.post("/v1/enhance", json={"prompt": "fix my code"})
    # Check the complete result
    assert response.status_code == 200
```

   **Slightly slower** — but covers the whole system

---

## 🤔 Special Case of Intelligent Router — Two Raju Bhais?

There is an interesting thing in Sahyog Restaurant. For **`POST /v1/chat`**:

1. First, **Ramesh Bhai** (Intent Intelligence) decides — "Is this a Biryani order or a Dal order?"
2. Then, **Raju Bhai** (Intelligent Router) makes the actual dish.

**But there's a problem:** Both Ramesh Bhai and Raju Bhai use the exact same **Gemini tandoor (oven)**!

If we set up different mocks for both:
```python
# ❌ WRONG — The second mock overwrites the first one!
patch("...intent_service.llm_provider.generate", AsyncMock(return_value=INTENT_JSON))
patch("...routing_service.llm_provider.generate", AsyncMock(return_value=EXECUTION))
# The second patch eats the first one — there's only one tandoor!
```

**Solution — `side_effect` list:**
```python
# ✅ CORRECT — INTENT_JSON on the first call, EXECUTION result on the second call
mock = AsyncMock(side_effect=[FAKE_INTENT_JSON, FAKE_EXECUTION_RESULT])
#                              ↑ 1st call         ↑ 2nd call

with patch("...intent_service.llm_provider.generate", new=mock):
    response = client.post("/v1/chat", ...)
```

> 🍛 **Restaurant Example:**
> Sharma Ji brought only one bag of dummy ingredients. First Ramesh Bhai checks it (intent), then Raju Bhai (routing). Same bag, two people, different jobs. The `side_effect` list tells them which item comes out first, and which one comes out later.

---

## 🏆 Our Final Inspection Report

After Sharma Ji's full inspection, Sahyog Restaurant received:

```text
🎉 CERTIFICATE OF APPROVAL — SAHYOG RESTAURANT 🎉

Inspection Date: 2026-05-29
Total Checks:    28
Passed:          28 ✅
Failed:           0 ❌

Special Note: The Inspector also caught a real production bug!
(Incorrect use of curly braces in system_prompt.py)
```

In Python, this looks like:

```text
===== 28 passed, 1 warning in 0.26s =====
```

---

## 📖 Quick Reference — Testing Dictionary

| Testing Term | Sahyog Restaurant Analogy |
|---|---|
| `pytest` | Sharma Ji (Food Safety Inspector) |
| Test file (`test_enhance.py`) | A specific inspection checklist |
| Test function (`def test_...`) | One item on the checklist |
| `assert` | "Is this correct?" — placing a checkmark |
| `AsyncMock` | Dummy ingredients (fake, but enough to test the process) |
| `patch()` | Replacing the real chef with a dummy chef |
| `conftest.py` | Sharma Ji's standard toolkit bag |
| `fixture` | A reusable tool that is helpful in every inspection |
| `PASSED` | ✅ Certificate of Approval |
| `FAILED` | ❌ Notice of Violation |
| `ERROR` | The inspection couldn't even start |
| `side_effect` list | Two different things in one bag — first one first, second one later |
