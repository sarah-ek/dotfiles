from conans import ConanFile


class BlazeConan(ConanFile):
    name = "blaze"
    version = "trunk"
    url = "https://bitbucket.org/blaze-lib/blaze/"
    homepage = "https://bitbucket.org/blaze-lib/blaze"
    license = "New (Revised) BSD license"
    description = "open-source, high-performance C++ math library for dense and sparse arithmetic"
    no_copy_source = True

    def source(self):
        self.run("git clone https://bitbucket.org/blaze-lib/blaze")

    def package(self):
        self.copy("*.h", src="blaze/blaze", dst="include/blaze")
