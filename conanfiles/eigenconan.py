from conans import ConanFile


class EigenConan(ConanFile):
    name = "eigen"
    version = "trunk"
    url = "https://gitlab.com/libeigen/eigen"
    homepage = "http://eigen.tuxfamily.org"
    license = "MPL-2.0"
    description = (
        "Eigen is a C++ template library for linear algebra: "
        "matrices, vectors, numerical solvers, and related algorithms."
    )
    no_copy_source = True

    def source(self):
        self.run("git clone https://gitlab.com/libeigen/eigen.git")

    def package(self):
        self.copy("*", src="eigen/Eigen", dst="include/Eigen")
        self.copy("*", src="eigen/unsupported/Eigen", dst="include/unsupported/Eigen")
