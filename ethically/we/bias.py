import copy

from .core import BiasWordsEmbedding
from .data import BOLUKBASI_DATA
from .utils import generate_one_word_forms, generate_words_forms


class GenderBiasWE(BiasWordsEmbedding):
    """Audit and Adjust the Gender Bias in English Words Embedding.

    :param model: Words embedding model of ``gensim.model.KeyedVectors``
    :param bool only_lower: Whether the words embedding contrains
                            only lower case words
    :param bool verbose: Set vebosity
    """

    def __init__(self, model, only_lower=False, verbose=False,
                 identify_direction=True):
        super().__init__(model, only_lower, verbose)
        self._initialize_data()
        if identify_direction:
            self._identify_direction('she', 'he',
                                     self._data['definitional_pairs'],
                                     'pca')

    def _initialize_data(self):
        self._data = copy.deepcopy(BOLUKBASI_DATA['gender'])

        if not self.only_lower:
            self._data['specific_full_with_definitional'] = \
                generate_words_forms(self
                                     ._data['specific_full_with_definitional'])  # pylint: disable=C0301

        for key in self._data['word_group_keys']:
            self._data[key] = (self._filter_words_by_model(self
                                                           ._data[key]))

        self._data['neutral_words'] = self._extract_neutral_words(self
                                                                  ._data['specific_full_with_definitional'])  # pylint: disable=C0301
        self._data['neutral_words'].sort()
        self._data['word_group_keys'].append('neutral_words')

    def plot_projection_scores(self, words='professions', n_extreme=10,
                               ax=None, axis_projection_step=None):
        if words == 'professions':
            words = self._data['profession_names']

        return super().plot_projection_scores(words, n_extreme,
                                              ax, axis_projection_step)

    def plot_dist_projections_on_direction(self, word_groups='bolukbasi',
                                           ax=None):
        if word_groups == 'bolukbasi':
            word_groups = {key: self._data[key]
                           for key in self._data['word_group_keys']}

        return super().plot_dist_projections_on_direction(word_groups, ax)

    @classmethod
    def plot_bias_across_words_embeddings(cls, words_embedding_bias_dict,
                                          ax=None, scatter_kwargs=None):
        # pylint: disable=W0221
        words = BOLUKBASI_DATA['gender']['neutral_profession_names']
        # TODO: is it correct for inhertence of class method?
        super(cls, cls).plot_bias_across_words_embeddings(words_embedding_bias_dict,  # pylint: disable=C0301
                                                          words,
                                                          ax,
                                                          scatter_kwargs)

    def calc_direct_bias(self, neutral_words='professions', c=None):
        if isinstance(neutral_words, str) and neutral_words == 'professions':
            return super().calc_direct_bias(
                self._data['neutral_profession_names'], c)
        else:
            return super().calc_direct_bias(neutral_words)

    def generate_closest_words_indirect_bias(self,
                                             neutral_positive_end,
                                             neutral_negative_end,
                                             words='professions', n_extreme=5):
        # pylint: disable=C0301

        if words == 'professions':
            words = self._data['profession_names']

        return super().generate_closest_words_indirect_bias(neutral_positive_end,
                                                            neutral_negative_end,
                                                            words,
                                                            n_extreme=n_extreme)

    def debias(self, method='hard', neutral_words=None, equality_sets=None,
               inplace=True):
        # pylint: disable=C0301
        if method in ['hard', 'neutralize']:
            if neutral_words is None:
                neutral_words = self._data['neutral_words']

        if method == 'hard' and equality_sets is None:
            equality_sets = self._data['definitional_pairs']

            if not self.only_lower:
                assert all(len(equality_set) == 2
                           for equality_set in equality_sets), 'currently supporting only equality pairs if only_lower is False'
                # TODO: refactor
                equality_sets = {(candidate1, candidate2)
                                 for word1, word2 in equality_sets
                                 for candidate1, candidate2 in zip(generate_one_word_forms(word1),
                                                                   generate_one_word_forms(word2))}

        return super().debias(method, neutral_words, equality_sets,
                              inplace)

    def learn_full_specific_words(self, seed_specific_words='bolukbasi',
                                  max_non_specific_examples=None,
                                  debug=None):
        if seed_specific_words == 'bolukbasi':
            seed_specific_words = self._data['specific_seed']

        return super().learn_full_specific_words(seed_specific_words,
                                                 max_non_specific_examples,
                                                 debug)
