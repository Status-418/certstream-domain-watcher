import re
import os.path

class fuzz_string(object):
    """ Domain fuzzer.
    """
    def __init__(self, domain):
        self.domain = domain
        self.domains = []
        self.qwerty = {
        '1': '2q', '2': '3wq1', '3': '4ew2', '4': '5re3', '5': '6tr4', '6': '7yt5', '7': '8uy6', '8': '9iu7', '9': '0oi8', '0': 'po9',
        'q': '12wa', 'w': '3esaq2', 'e': '4rdsw3', 'r': '5tfde4', 't': '6ygfr5', 'y': '7uhgt6', 'u': '8ijhy7', 'i': '9okju8', 'o': '0plki9', 'p': 'lo0',
        'a': 'qwsz', 's': 'edxzaw', 'd': 'rfcxse', 'f': 'tgvcdr', 'g': 'yhbvft', 'h': 'ujnbgy', 'j': 'ikmnhu', 'k': 'olmji', 'l': 'kop',
        'z': 'asx', 'x': 'zsdc', 'c': 'xdfv', 'v': 'cfgb', 'b': 'vghn', 'n': 'bhjm', 'm': 'njk'
        }
        self.qwertz = {
        '1': '2q', '2': '3wq1', '3': '4ew2', '4': '5re3', '5': '6tr4', '6': '7zt5', '7': '8uz6', '8': '9iu7', '9': '0oi8', '0': 'po9',
        'q': '12wa', 'w': '3esaq2', 'e': '4rdsw3', 'r': '5tfde4', 't': '6zgfr5', 'z': '7uhgt6', 'u': '8ijhz7', 'i': '9okju8', 'o': '0plki9', 'p': 'lo0',
        'a': 'qwsy', 's': 'edxyaw', 'd': 'rfcxse', 'f': 'tgvcdr', 'g': 'zhbvft', 'h': 'ujnbgz', 'j': 'ikmnhu', 'k': 'olmji', 'l': 'kop',
        'y': 'asx', 'x': 'ysdc', 'c': 'xdfv', 'v': 'cfgb', 'b': 'vghn', 'n': 'bhjm', 'm': 'njk'
        }
        self.azerty = {
        '1': '2a', '2': '3za1', '3': '4ez2', '4': '5re3', '5': '6tr4', '6': '7yt5', '7': '8uy6', '8': '9iu7', '9': '0oi8', '0': 'po9',
        'a': '2zq1', 'z': '3esqa2', 'e': '4rdsz3', 'r': '5tfde4', 't': '6ygfr5', 'y': '7uhgt6', 'u': '8ijhy7', 'i': '9okju8', 'o': '0plki9', 'p': 'lo0m',
        'q': 'zswa', 's': 'edxwqz', 'd': 'rfcxse', 'f': 'tgvcdr', 'g': 'yhbvft', 'h': 'ujnbgy', 'j': 'iknhu', 'k': 'olji', 'l': 'kopm', 'm': 'lp',
        'w': 'sxq', 'x': 'zsdc', 'c': 'xdfv', 'v': 'cfgb', 'b': 'vghn', 'n': 'bhj'
        }
        self.keyboards = [ self.qwerty, self.qwertz, self.azerty ]

    def __bitsquatting(self):
        result = []
        masks = [1, 2, 4, 8, 16, 32, 64, 128]
        for i in range(0, len(self.domain)):
            c = self.domain[i]
            for j in range(0, len(masks)):
                b = chr(ord(c) ^ masks[j])
                o = ord(b)
                if (o >= 48 and o <= 57) or (o >= 97 and o <= 122) or o == 45:
                    result.append(self.domain[:i] + b + self.domain[i+1:])

        return result

    def __homoglyph(self):
        glyphs = {
        'd': ['b', 'cl', 'dl', 'di'], 'm': ['n', 'nn', 'rn', 'rr'], 'l': ['1', 'i'],
        'o': ['0'], 'k': ['lk', 'ik', 'lc'], 'h': ['lh', 'ih'], 'w': ['vv'],
        'n': ['m', 'r'], 'b': ['d', 'lb', 'ib'], 'i': ['1', 'l'], 'g': ['q'], 'q': ['g']
        }
        result = []

        for ws in range(0, len(self.domain)):
            for i in range(0, (len(self.domain)-ws)+1):
                win = self.domain[i:i+ws]

                j = 0
                while j < ws:
                    c = win[j]
                    if c in glyphs:
                        win_copy = win
                        for g in glyphs[c]:
                            win = win.replace(c, g)
                            result.append(self.domain[:i] + win + self.domain[i+ws:])
                            win = win_copy
                    j += 1

        return list(set(result))

    def __hyphenation(self):
        result = []

        for i in range(1, len(self.domain)):
            if self.domain[i] not in ['-', '.'] and self.domain[i-1] not in ['-', '.']:
                result.append(self.domain[:i] + '-' + self.domain[i:])

        return result

    def __insertion(self):
        result = []

        for i in range(1, len(self.domain)-1):
            for keys in self.keyboards:
                if self.domain[i] in keys:
                    for c in keys[self.domain[i]]:
                        result.append(self.domain[:i] + c + self.domain[i] + self.domain[i+1:])
                        result.append(self.domain[:i] + self.domain[i] + c + self.domain[i+1:])

        return list(set(result))

    def __omission(self):
        result = []

        for i in range(0, len(self.domain)):
            result.append(self.domain[:i] + self.domain[i+1:])

        n = re.sub(r'(.)\1+', r'\1', self.domain)

        if n not in result and n != self.domain:
            result.append(n)

        return list(set(result))

    def __repetition(self):
        result = []

        for i in range(0, len(self.domain)):
            if self.domain[i].isalpha():
                result.append(self.domain[:i] + self.domain[i] + self.domain[i] + self.domain[i+1:])

        return list(set(result))

    def __replacement(self):
        result = []

        for i in range(0, len(self.domain)):
            for keys in self.keyboards:
                if self.domain[i] in keys:
                    for c in keys[self.domain[i]]:
                        result.append(self.domain[:i] + c + self.domain[i+1:])

        return list(set(result))

    def __vowel_swap(self):
        vowels = 'aeiou'
        result = []

        for i in range(0, len(self.domain)):
            for vowel in vowels:
                if self.domain[i] in vowels:
                    result.append(self.domain[:i] + vowel + self.domain[i+1:])

        return list(set(result))

    def __subdomain(self):
        result = []

        for i in range(1, len(self.domain)):
            if self.domain[i] not in ['-', '.'] and self.domain[i-1] not in ['-', '.']:
                result.append(self.domain[:i] + '.' + self.domain[i:])

        return result

    def __transposition(self):
        result = []

        for i in range(0, len(self.domain)-1):
            if self.domain[i+1] != self.domain[i]:
                result.append(self.domain[:i] + self.domain[i+1] + self.domain[i] + self.domain[i+2:])

        return result

    def __addition(self):
        result = []

        for i in range(97, 123):
            result.append(self.domain + chr(i))

        return result

    def fuzz(self):
        """ Perform a domain fuzz.
        """
        self.domains.append({ 'fuzzer': 'Original*', 'domain-name': self.domain})
        for domain in self.__addition():
            self.domains.append({ 'fuzzer': 'Addition', 'domain-name': domain})
        for domain in self.__bitsquatting():
            self.domains.append({ 'fuzzer': 'Bitsquatting', 'domain-name': domain})
        for domain in self.__homoglyph():
            self.domains.append({ 'fuzzer': 'Homoglyph', 'domain-name': domain})
        for domain in self.__hyphenation():
            self.domains.append({ 'fuzzer': 'Hyphenation', 'domain-name': domain})
        for domain in self.__insertion():
            self.domains.append({ 'fuzzer': 'Insertion', 'domain-name': domain})
        for domain in self.__omission():
            self.domains.append({ 'fuzzer': 'Omission', 'domain-name': domain})
        for domain in self.__repetition():
            self.domains.append({ 'fuzzer': 'Repetition', 'domain-name': domain})
        for domain in self.__replacement():
            self.domains.append({ 'fuzzer': 'Replacement', 'domain-name': domain})
        for domain in self.__subdomain():
            self.domains.append({ 'fuzzer': 'Subdomain', 'domain-name': domain})
        for domain in self.__transposition():
            self.domains.append({ 'fuzzer': 'Transposition', 'domain-name': domain})
        for domain in self.__vowel_swap():
            self.domains.append({ 'fuzzer': 'Vowel swap', 'domain-name': domain})

        if not self.domain.startswith('www.'):
            self.domains.append({ 'fuzzer': 'Various', 'domain-name': 'ww' + self.domain})# + '.' + self.tld })
            self.domains.append({ 'fuzzer': 'Various', 'domain-name': 'www' + self.domain})# + '.' + self.tld })
            self.domains.append({ 'fuzzer': 'Various', 'domain-name': 'www-' + self.domain})# + '.' + self.tld })


if __name__ == "__main__":
    fuzzer = fuzz_domain('qualcomm')
    fuzzer.fuzz()
    for fdomain in (list(fuzzer.domains)):
       print(fdomain['domain-name'].strip())

