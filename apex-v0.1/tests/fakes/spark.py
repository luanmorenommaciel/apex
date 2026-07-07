class FakeLoadedDataFrame:
    def __init__(self, path):
        self.path = path


class FakeReader:
    def __init__(self, dataset_format):
        self.dataset_format = dataset_format
        self.options = []
        self.loaded_path = None

    def option(self, key, value):
        self.options.append((key, value))
        return self

    def load(self, path):
        self.loaded_path = path
        return FakeLoadedDataFrame(path)


class FakeReadRoot:
    def __init__(self):
        self.readers = []

    def format(self, dataset_format):
        reader = FakeReader(dataset_format)
        self.readers.append(reader)
        return reader


class FakeSparkSession:
    def __init__(self):
        self.read = FakeReadRoot()


class FakeWriter:
    def __init__(self, dataset_format):
        self.dataset_format = dataset_format
        self.mode_value = None
        self.options = []
        self.partition_columns = ()
        self.saved_path = None

    def mode(self, mode):
        self.mode_value = mode
        return self

    def option(self, key, value):
        self.options.append((key, value))
        return self

    def partitionBy(self, *columns):
        self.partition_columns = columns
        return self

    def save(self, path):
        self.saved_path = path


class FakeWriteRoot:
    def __init__(self):
        self.writers = []

    def format(self, dataset_format):
        writer = FakeWriter(dataset_format)
        self.writers.append(writer)
        return writer


class FakeDataFrame:
    def __init__(self):
        self.write = FakeWriteRoot()
