import requests
import cursus


def create_coursematerial():
    """
    Modifies the info of the course material on the site and downloads the front page.
    :return: front page or None (error)
    """
    c = cursus.Cursus(True, 25011, 100, 0, True, 10, 10.3)
    print(c.get_json())
    r = requests.post('vtk.be/api/cudi/is-same', json=c.get_json())
    print(r.status_code)
    print(r.json())


create_coursematerial()
