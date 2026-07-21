Source: https://www.ardanlabs.com/blog/2017/02/package-oriented-design.html

# Package Oriented Design

Updated on February 28th, 2017

### Prelude

This post is part of a series of posts designed to make you think about your own design philosophy on different topics. If you haven’t read these posts yet, please do so first:

Develop Your Design PhilosophyDesign Philosophy On Packaging

### Introduction

Package Oriented Design allows a developer to identify where a package belongs inside a Go project and the design guidelines the package must respect. It defines what a Go project is and how a Go project is structured. Finally, it improves communication between team members and promotes clean package design and project architecture that is discussable.

Package oriented design is NOT bound to a single project structure, but states that a project structure is paramount to applying guidelines for good package design. Moving forward, I will present one possible project structure and the guidelines to follow based on the design philosophies presented earlier.

### Project Structure

I believe that every company should establish a single Kit project and then multiple Application projects for the different sets of programs that get deployed together.

#### Kit Projects

Think of the Kit project as a company’s standard library, so there should only be one. The packages that belong to the Kit project need to be designed with the highest levels of portability in mind. These packages should be usable across multiple Application projects and provide a very specific but foundational domain of functionality. If any of packages are dependent on 3rd party packages, they must always build against the latest version of those dependences.

A typical Kit project might look like this:

Listing 1

```
github.com/ardanlabs/kit
├── CONTRIBUTORS
├── LICENSE
├── README.md
├── cfg/
├── examples/
├── log/
├── pool/
├── tcp/
├── timezone/
├── udp/
└── web/
```

Note: There is nothing wrong with breaking each of these Kit packages into their own repository. I don’t do this because it creates more work managing all these packages.

#### Application Projects

Application projects contain the set of programs that get deployed together. The set of programs can include services, cli tooling and background programs. Each Application project is bound to a single repo that contains all the source code for that project, including all the source code for the 3rd party dependencies. How many Application projects you need is up to you, but always take a less is more approach.

Each Application project contains cmd/ and internal/ folders.

A typical Application project might look like this:

Listing 2

```
github.com/servi-io/api
├── cmd/
│   ├── servi/
│   │   ├── cmdupdate/
│   │   ├── cmdquery/
│   │   └── servi.go
│   └── servid/
│       ├── routes/
│       │   └── handlers/
│       ├── tests/
│       └── servid.go
└── internal/
    ├── attachments/
    ├── locations/
    ├── orders/
    │   ├── customers/
    │   ├── items/
    │   ├── tags/
    │   └── orders.go
    └── registrations/
```

#### cmd/

All the programs this project owns belongs inside the cmd/ folder. The folders under cmd/ are always named for each program that will be built. Use the letter d at the end of a program folder to denote it as a daemon. Each folder has a matching source code file that contains the main package.

#### internal/

Packages that need to be imported by multiple programs within the project belong inside the internal/ folder. One benefit of using the name internal/ is that the project gets an extra level of protection from the compiler. No package outside of this project can import packages from inside of internal/. These packages are therefore internal to this project only.

### Validate Package Design

An important aspect of package oriented design is the ability to validate the design of packages. This is possible because of the guidelines that are associated with a package based on its location inside the project. There are seven validation steps that will help you identify design problems.

#### Validate the location of a package.

- KitPackages that provide foundational support for the different Application projects that exist.logging, configuration or web functionality.
- cmd/Packages that provide support for a specific program that is being built.startup, shutdown and configuration.
- internal/Packages that provide support for the different programs the project owns.CRUD, services or business logic.

#### Validate the dependency choices.

- AllValidate the cost/benefit of each dependency.Question imports for the sake of sharing existing types.Question imports to others packages at the same level.If a package wants to import another package at the same level:Question the current design choices of these packages.If reasonable, move the package inside the source tree for the package that wants to import it.Use the source tree to show the dependency relationships.
- internal/Packages from these locations CAN’T be imported:cmd/

#### Validate the policies being imposed.

- Kit: NOT allowed to set policy about any application concerns.NOT allowed to log, but access to trace information must be decoupled.Configuration and runtime changes must be decoupled.Retrieving metric and telemetry values must be decoupled.
- cmd/, internal/Allowed to set policy about any application concerns.Allowed to log and handle configuration natively.

#### Validate how data is accepted/returned.

- AllValidate the consistent use of value/pointer semantics for a given type.When using an interface type to accept a value, the focus must be on the behavior that is required and not the value itself.If behavior is not required, use a concrete type.When reasonable, use an existing type before declaring a new one.Question types from dependencies that leak into the exported API.An existing type may no longer be reasonable to use.

#### Validate how errors are handled.

- AllHandling an error means:The error has been logged.The application is back to 100% integrity.The current error is not reported any longer.
- KitNOT allowed to panic an application.NOT allowed to wrap errors.Return only root cause error values.
- cmd/Allowed to panic an application.Wrap errors with context if not being handled.Majority of handling errors happen here.
- internal/NOT allowed to panic an application.Wrap errors with context if not being handled.Minority of handling errors happen here.

#### Validate testing.

- cmd/Allowed to use 3rd party testing packages.Can have a test folder for tests.Focus more on integration than unit testing.
- kit/, internal/Stick to the testing package in go.Test files belong inside the package.Focus more on unit than integration testing.

#### Validate recovering panics.

- cmd/Can recover any panic.Only if system can be returned to 100% integrity.
- kit/, internal/Can not recover from panics unless:Goroutine is owned by the package.Can provide an event to the app about the panic.

### Quick Example

Here is a quick example of how we can review the Application project to understand how the project is put together and validate the dependency choices for each package.

- cmd/This Application project builds two programs: servi and servid.servid is a web service.servi is a cli tool.None of the packages inside of servid/ can import any packages from inside servi/.The routes package CAN’T import the cmdupdate package.The routes package does import the handlers package.
- internal/This project has four root level internal packages.attachments, locations, orders and registrations.The four root level packages are not allowed to import each other.They are at the same level.attachments can’t import any other internal/ only package.The orders package has three packages declared inside of it.customers, items and tags.From within the internal/ folder, only orders can import these packages.These three packages can’t import each other.

### Conclusion

Package Oriented Design fosters conversations and review to make sure packages maintain the best possible purpose, usability and portability. This drives clean package design for any package across the entire project. For package oriented design to be effective, you need strong rules about project structure. The project structure I have shared has been developed over the past three years and has been working effectively on multiple projects. Other project structures could be just as effective and I expect over time to continue to refactor my project structure and guidelines.

My goal in everything I teach is to get you to start thinking about what you are doing and why. To have you start asking questions and validate everything you are doing. I hope you start to think about package oriented design and begin to formalize how you structure projects and design packages for the projects you work on.