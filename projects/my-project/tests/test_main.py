from my_project.main import main

def test_main(test_settings):
    result = main()
    assert "Hello, MyProject!" in result
