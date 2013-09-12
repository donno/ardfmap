
import interface

def printGeometry(service):
  for g in service.allGeometry():
    print g

def main():
  apiBaseUri = "http://localhost:8083/api/"
  service = interface.Interface(apiBaseUri)

  # Print out all the geometry.
  #printGeometry(service)

  # Create a new line.
  o = service.createLine(points=[(100.0, 0.0), (101.0, 1.0)])

  # This replaces all the points in the line.
  service.updateLine(o, points=[(200.0, 0.0), (101.0, 1.0)])

if __name__ == "__main__":
  main()