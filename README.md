# Code Improvement Learning App

This is a PyQt6-based desktop application designed to help users improve their coding skills by identifying and correcting bad code examples.

## Features

- Generate bad code examples for a specified area of improvement
- Allow users to annotate and comment on the bad code
- Provide feedback on user annotations
- Score user performance across multiple examples
- Generate humorous feedback at the end of the session

## Requirements

- Python 3.6+
- PyQt6
- anthropic

## Installation

1. Clone this repository:
   ```
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Install the required packages:
   ```
   pip install PyQt6 anthropic
   ```

3. Set up your Anthropic API key:
   - Sign up for an account at https://www.anthropic.com
   - Obtain your API key
   - When you run the application, you'll be prompted to enter your Anthropic API key in the top-right corner of the app window

## Running the App

To run the application, execute the following command in your terminal:

```
python code_improvement_app.py
```

When the application starts, you'll see an input field in the top-right corner where you should enter your Anthropic API key. The application requires a valid API key to function properly.

## How to Use

1. Enter an area of code you want to improve in the "Enter area to improve" field.
2. Click "Create Example" to generate a bad code example.
3. Review the generated code and add your comments or annotations in the same text area.
4. Click "Submit" to get feedback on your annotations.
5. Review the feedback provided.
6. Click "Next Example" to move to the next question (if available). This will generate a new bad code example for the same area.
7. Repeat steps 3-6 for the remaining examples.
8. After completing all examples, you'll receive a humorous overall feedback message.

## Note

This application uses the Anthropic API to generate code examples and provide feedback. Ensure you have a stable internet connection while using the app.
