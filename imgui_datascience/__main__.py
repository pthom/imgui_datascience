import sys
from . import example

def main(args=None):
    if args is None:
        args = sys.argv[1:]
    print("(py)imgui for datascience (https://github.com/pthom/imgui_datascience)")
    print("Run the example with the following command:")
    print("python -m imgui_datascience --example")
    if "--example" in args:
        example.example()

if __name__ == "__main__":
    main()
