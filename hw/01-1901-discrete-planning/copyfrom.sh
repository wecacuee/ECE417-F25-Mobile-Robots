SRC_ROOT= ../../../ECE417-solution-notebooks
SRC_DIR=${SRC_ROOT}/source/01-1901-discrete-planning/
cp ${SRC_DIR}/dist/student/HW2_BFSDijkstraAndPriorityQueue.ipynb HW2_BFSDijkstraAndPriorityQueue.ipynb
cd ${SRC_DIR}/dist/student/ && zip -r ../HW2_BFSDijkstraAndPriorityQueue.ipynb_assets.zip imgs/ tests/ && cd -
cp ${SRC_DIR}/dist/HW2_BFSDijkstraAndPriorityQueue.ipynb_assets.zip HW2_BFSDijkstraAndPriorityQueue.ipynb_assets.zip
