const vscode = require("vscode");
const { exec } = require("child_process");

function activate(context) {
  let disposable = vscode.commands.registerCommand(
    "rag.askQuestion",
    function () {
      vscode.window
        .showInputBox({ prompt: "Ask a modernization question" })
        .then((question) => {
          if (!question) return;

          exec(
            `python rag_engine.py "${question}"`,
            (error, stdout, stderr) => {
              if (error) {
                vscode.window.showErrorMessage("Error running RAG");
                return;
              }
              vscode.window.showInformationMessage(stdout);
            }
          );
        });
    }
  );

  context.subscriptions.push(disposable);
}

function deactivate() {}

module.exports = {
  activate,
  deactivate
};
