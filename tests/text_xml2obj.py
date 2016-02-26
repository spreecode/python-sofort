import unittest

import sofort.xml2obj


class XmlResponseTest(unittest.TestCase):
    def test_simple(self):
        book = sofort.xml2obj.fromstring("""
            <book>
                <author>
                    <first_name>Lev</first_name>
                    <last_name>Tolstoy</last_name>
                </author>
            </book>
            """)
        self.assertEqual('Lev', book.author.first_name)
        self.assertEqual('Tolstoy', book.author.last_name)

    def test_simple_array_collapse(self):
        book = sofort.xml2obj.fromstring("""
            <book>
                <author>
                    <books>
                        <book>Anna Karenina</book>
                        <book>War and Peace</book>
                        <book>Resurrection</book>
                    </books>
                </author>
                <volumes>
                    <volume>I</volume>
                    <volume>II</volume>
                    <volume>III</volume>
                    <volume>IV</volume>
                </volumes>
            </book>
            """)
        self.assertEqual(4, len(book.volumes))
        self.assertEqual(3, len(book.author.books))
        self.assertEqual('I', book.volumes[0])

    def test_nested_array_collapse(self):
        book = sofort.xml2obj.fromstring("""
            <book>
                <chars>
                    <char>
                        <names>
                            <name>Pyotr Bezrukov</name>
                            <name>Pierre Bezrukov</name>
                        </names>
                    </char>
                    <char>
                        <names>
                            <name>Andrei Bolkonsky</name>
                        </names>
                    </char>
                </chars>
            </book>
            """)
        self.assertEqual('Pyotr Bezrukov', book.chars[0].names[0])
        self.assertEqual('Pierre Bezrukov', book.chars[0].names[1])
        self.assertEqual('Andrei Bolkonsky', book.chars[1].names[0])

    def test_mixed_arrays(self):
        book = sofort.xml2obj.fromstring("""
            <book>
                <mixeds>
                    <mixed>List1</mixed>
                    <mixed>List2</mixed>
                    <extra>Corrupt</extra>
                </mixeds>
            </book>
            """)
        self.assertEqual('List1', book.mixeds.mixed[0])
        self.assertEqual('List2', book.mixeds.mixed[1])
        self.assertEqual('Corrupt', book.mixeds.extra)
