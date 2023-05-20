import unittest

from app.server.tests import test_database, test_presentation_processing

if __name__ == '__main__':
    loader = unittest.TestLoader()

    db_suite = loader.loadTestsFromModule(test_database)
    unittest.TextTestRunner(verbosity=2).run(db_suite)

    pres_processing_suite = loader.loadTestsFromModule(test_presentation_processing)
    unittest.TextTestRunner(verbosity=2).run(pres_processing_suite)