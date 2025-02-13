import unittest, sys, os
from unittest.mock import Mock
from dataclasses import dataclass
from typing import List
import helm_wrap
from hwrap_settings import REAL_HELM, HARBOR_HOST

class TestBuildCommand(unittest.TestCase):
 
    def setUp(self):
        helm_wrap.get_handles = Mock(return_value={'bitnami': "https://charts.bitnami.com/bitnami"})
        helm_wrap.analyze_install_handle = Mock(return_value=['mariadb', True])
        return super().setUp()
    

    def test_table_test(self):
        @dataclass
        class TestCase:
            name: str
            input: str
            expected: List[str]

        testcases = [
            TestCase(
                name = "version",
                input = "helm version",
                expected=[REAL_HELM, "version"],            
            ),
            TestCase(
                name = "install bitnami",
                input = "helm install test1 bitnami/mariadb",
                expected=[REAL_HELM, "install", "test1",
                         f"oci://{HARBOR_HOST}/bitnami/mariadb"
                    ],            
            ),
            TestCase(
                name = "install not bitnami",
                input = "helm install test2 salami/mariadb",
                expected=[REAL_HELM, "install", "test2",
                         "salami/mariadb"
                    ],            
            ),
            TestCase(
                name = "repo list",
                input = "helm repo list",
                expected=[REAL_HELM, "repo", "list",]
            ),
            TestCase(
                name = "helm pull",
                input = "helm pull bitnami/mariadb",
                expected=[REAL_HELM, "pull",
                         f"oci://{HARBOR_HOST}/bitnami/mariadb"
                    ],            
            ),
            TestCase(
                name = "helm upgrade",
                input = "helm upgrade test1  bitnami/mariadb --version 1.10",
                expected=[REAL_HELM, "upgrade", "test1",
                         f"oci://{HARBOR_HOST}/bitnami/mariadb",
                         "--version", "1.10"
                    ],            
            ),

            TestCase(
                name = "helm upgrade non-bitnami",
                input = "helm upgrade test1  salami/mariadb --version 1.10",
                expected=[REAL_HELM, "upgrade", "test1",
                         "salami/mariadb",
                         "--version", "1.10"
                    ],            
            ),

          
            # handling flags

            TestCase(
                name = "install not bitnami, namespace late",
                input = "helm install test2  --namespace appspace salami/mariadb",
                expected=[REAL_HELM, "install", "test2",
                          "salami/mariadb",
                          "--namespace", "appspace",
                    ],            
            ),
            
            TestCase(
                name = "install not bitnami, namespace early",
                input = "helm install -n appspace test2 salami/mariadb",
                expected=[REAL_HELM, "install", 
                          "test2",
                          "salami/mariadb",
                          "-n", "appspace",
                    ],            
            ),
            
            TestCase(
                name = "install dry-run not bitnami",
                input = "helm install --dry-run test2 salami/mariadb",
                expected=[REAL_HELM, "install", 
                          "test2",
                          "salami/mariadb",
                          "--dry-run",
                    ],            
            ),




        ]

        for case in testcases:
            args = case.input.split()
            rslt = helm_wrap.build_command(args)
            print("")
            returned = rslt.split()
            ndx = 0
            for val in case.expected:
                if val != "":
                    self.assertGreater(
                        len(returned),
                        ndx,
                        f"Case '{case.name}': returned {len(returned)} args, expected at least {len(case.expected)}",
                    )                        
                    self.assertEqual(
                        returned[ndx], 
                        val,
                        f"Case '{case.name}',\n\tPassed: {case.input}\n\tReturned: {rslt}\n\targ {ndx}: expected {case.expected[ndx]}, got {returned[ndx]}"
                    )
                ndx += 1


if __name__ == '__main__':
    # Execute when the module is not initialized from an import statement.
    if 'DEBUG_WRAPPER_TEST' in os.environ:
        import debugpy
        debugpy.listen(('0.0.0.0', 5678))
        print("Waiting for debugger attach", file=sys.stderr)
        debugpy.wait_for_client()

    unittest.main()
