# J.A.I.son Component Template
This is a template to make components for Project J.A.I.son.

## What is a component?
A component is something the core of Project J.A.I.son uses to generate responses. These are hot-swappable implementations designed for users to pick and choose which e.g. model they want to use in the project. These are mainly intended to be adapters for models and APIs, but these can be extended to anything.

These components support **AND ENCOURAGE** the use of data-streaming. When possible, model implementations should stream back their results using [python generators](https://wiki.python.org/moin/Generators)

## How does this work?
[`jaison-core`](https://github.com/limitcantcode/jaison-core) will use either `start.bat` for Windows or `start.sh` for Unix-like systems to load the right virtual environment and run the component on the specified port.

The actual component runs a [GRPC](https://github.com/grpc/grpc) server that uses the configured component to transform data.

## What do I do?
1. Minimum dependencies are found in `requirements.txt`. You can install them using `pip install -r requirements.txt`. Please ensure you do this in a (python or conda) virtual environment.

2. Update `metadata.yaml` with your project-specific information.

3. Implement your model in `src/custom/__init__.py`. Pick out the associated function that was configured in step 2 and implement that one. Other ones can remain blank.

4. Update the `start` scripts to run the component starting from the root directory. This should include loading the right virtual environment given the user followed the setup steps you define in the next step. If your component can only run on either Windows or Unix machines, `metadata.yaml` should reflect this and the associated start script won't be used.

5. Fill out the `README-template.md` with details about this project, and most importantly **how to set up the project with the correct virtual environment to run the component.** If there are other special restrictions like hardware or other special setup instructions, state them there.

6. Cleanup the project (replacing this `README.md` with the new `README-template.md`, removing `CONTRIBUTING.md`, etc.).

7. Upload to Github and share your work on the [Discord server](https://discord.gg/Z8yyEzHsYM) so we can add you component to the list of implementations for everyone to use!

## Contributing
I am accepting contributions for this package. If you would like to contribute, please refer to [CONTRIBUTING](https://github.com/limitcantcode/jaison-grpc/tree/main/CONTRIBUTING.md).