# Init
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run
export OPENAI_API_KEY=sk-********************
export GITHUB_TOKEN=*******************
python3 main.py

# Workflow
download code from github -> create code indexs & log indexs -> query error from log indexs -> query error from code indexs -> given solution

# Example Data:
logs - > ./data/log/*.log
source code -> https://github.com/DevYoungHulk/spring-demo.git

# Example Question:
Find the key error messages in the logs and query the relevant lines of code based on the error messages to provide solutions

# Example Output:
Added user message to memory: Find the key error messages in the logs and query the relevant lines of code based on the error messages to provide solutions
=== Calling Function ===
Calling function: log_vector_tool with args: {
  "input": "error"
}
Got output: The error mentioned in the context is a "java.lang.NullPointerException".
========================

=== Calling Function ===
Calling function: code_vector_tool with args: {
  "input": "java.lang.NullPointerException"
}
Got output: The code snippet provided in the context contains a method called "NullError" in the "DemoController" class. This method intentionally throws a `java.lang.NullPointerException` by trying to call the `toString()` method on a null object.
========================

Based on the error message "java.lang.NullPointerException", it seems that there is a `NullPointerException` occurring in the code. The relevant code snippet is from the `DemoController` class and the method causing the error is `NullError`.

Here is the code snippet:

```java
public class DemoController {
    public void NullError() {
        Object obj = null;
        String str = obj.toString(); // NullPointerException occurs here
    }
}
```

In this code, the `NullError` method is intentionally throwing a `NullPointerException` by trying to call the `toString()` method on a null object (`obj`). To fix this issue, you need to ensure that the object is not null before calling any methods on it.

One possible solution is to add a null check before calling the `toString()` method. Here's an updated version of the code:

```java
public class DemoController {
    public void NullError() {
        Object obj = null;
        if (obj != null) {
            String str = obj.toString();
        } else {
            // Handle the case when obj is null
            // For example, you can log an error message or throw a custom exception
        }
    }
}
```

By adding the null check, the code will only call the `toString()` method if the `obj` is not null, preventing the `NullPointerException` from occurring.