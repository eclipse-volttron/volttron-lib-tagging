# -*- coding: utf-8 -*- {{{
# ===----------------------------------------------------------------------===
#
#                 Installable Component of Eclipse VOLTTRON
#
# ===----------------------------------------------------------------------===
#
# Copyright 2022 Battelle Memorial Institute
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy
# of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
#
# ===----------------------------------------------------------------------===
# }}}
"""
pytest test cases for tagging service
"""
from abc import abstractmethod
from datetime import datetime

import gevent
import pytest

from volttron.utils.jsonrpc import RemoteError
from volttron.utils import format_timestamp
from volttron.client.messaging import headers as headers_mod


class TaggingTestInterface:

    @pytest.fixture(scope="module")
    def historian(self, volttron_instance):
        config = {
            "connection": {
                "type": "sqlite",
                "params": {
                    "database": volttron_instance.volttron_home + '/test.sqlite'
                }
            }
        }
        historian_uuid = volttron_instance.install_agent(
            vip_identity='platform.historian',
            agent_dir="volttron-sqlite-historian",
            config_file=config,
            start=True)
        gevent.sleep(1)
        yield 'platform.historian'
        if volttron_instance.is_running() and volttron_instance.is_agent_running(historian_uuid):
            volttron_instance.remove_agent(historian_uuid)

    @pytest.fixture(scope="module")
    def tagging_agent(self):
        """ Inheriting test classes should install an instance of tagging agent for test and return the vip identity """
        pass

    @abstractmethod
    def cleanup(self, truncate_tables, drop_tables=False):
        """
        truncate or drop the list of tables passed or if no list is passed all tables in db
        """
        pass

    @pytest.fixture(scope="module")
    def query_agent(self, volttron_instance):
        # 1: Start a fake agent to query the historian agent in volttron_instance
        agent = volttron_instance.build_agent()
        yield agent
        print("In teardown method of fake_agent")
        agent.core.stop()

    def test_get_categories_no_desc(self, tagging_agent, query_agent):
        result = query_agent.vip.rpc.call(tagging_agent, 'get_categories',
                                          skip=0, count=4,
                                          order="FIRST_TO_LAST").get(timeout=10)
        assert isinstance(result, list)
        assert len(result) == 4
        print("Categories returned: {}".format(result))
        result2 = query_agent.vip.rpc.call(tagging_agent, 'get_categories',
                                           skip=1, count=4,
                                           order="FIRST_TO_LAST").get(timeout=10)
        assert isinstance(result2, list)
        print("result2 returned: {}".format(result2))
        assert len(result2) == 4
        assert isinstance(result, list)
        assert isinstance(result[0], str)
        assert result[1] == result2[0]  # verify skip

    def test_get_categories_with_desc(self, tagging_agent, query_agent):
        result1 = query_agent.vip.rpc.call(tagging_agent, 'get_categories',
                                           include_description=True, skip=0,
                                           count=4, order="LAST_TO_FIRST").get(
            timeout=10)
        assert isinstance(result1, list)
        assert isinstance(result1[0], list)
        assert len(result1) == 4
        assert len(result1[0]) == 2
        print("Categories returned: {}".format(result1))
        result2 = query_agent.vip.rpc.call(tagging_agent, 'get_categories',
                                           include_description=True, skip=1,
                                           count=4, order="LAST_TO_FIRST").get(
            timeout=10)
        assert isinstance(result2, list)
        assert len(result2) == 4
        assert isinstance(result2[0], list)
        print("result2 returned: {}".format(result2))

        # Verify skip param
        assert result1[1][0] == result2[0][0]
        assert result1[1][1] == result2[0][1]

        # verify order
        result3 = query_agent.vip.rpc.call(tagging_agent, 'get_categories',
                                           include_description=True, skip=0,
                                           count=4, order="FIRST_TO_LAST").get(
            timeout=10)
        assert isinstance(result3, list)
        assert len(result3) == 4
        assert isinstance(result3[0], list)
        assert result3[0][0] != result1[0][0]
        assert result3[0][1] != result1[0][1]

    def test_tags_by_category_no_metadata(self, tagging_agent, query_agent):
        result1 = query_agent.vip.rpc.call(
            tagging_agent, 'get_tags_by_category', category='AHU', skip=0,
            count=3, order="FIRST_TO_LAST").get(timeout=10)
        print("tags returned: {}".format(result1))
        assert isinstance(result1, list)
        assert len(result1) == 3
        assert isinstance(result1[0], str)

        result2 = query_agent.vip.rpc.call(tagging_agent,
                                           'get_tags_by_category', category='AHU',
                                           skip=2, count=3,
                                           order="FIRST_TO_LAST").get(timeout=10)
        print("tags returned: {}".format(result2))
        assert isinstance(result2, list)
        assert len(result2) == 3  # verify count
        assert isinstance(result2[0], str)
        assert result1[2] == result2[0]  # verify skip

    def test_tags_by_category_with_metadata(self, tagging_agent, query_agent):
        result1 = query_agent.vip.rpc.call(
            tagging_agent, 'get_tags_by_category', category='AHU',
            include_kind=True, skip=0, count=3,
            order="FIRST_TO_LAST").get(timeout=10)
        print("tags returned: {}".format(result1))
        assert isinstance(result1, list)
        assert len(result1) == 3
        assert isinstance(result1[0], list)
        assert len(result1[0]) == 2

        result2 = query_agent.vip.rpc.call(
            tagging_agent, 'get_tags_by_category',
            category='AHU', include_description=True,
            skip=0, count=3, order="FIRST_TO_LAST").get(timeout=10)
        print("tags returned: {}".format(result2))
        assert isinstance(result2, list)
        assert len(result2) == 3
        assert isinstance(result2[0], list)
        assert len(result2[0]) == 2

        result3 = query_agent.vip.rpc.call(
            tagging_agent, 'get_tags_by_category', category='AHU',
            include_kind=True, include_description=True, skip=0,
            count=3, order="FIRST_TO_LAST").get(timeout=10)
        print("tags returned: {}".format(result3))
        assert isinstance(result3, list)
        assert len(result3) == 3
        assert isinstance(result3[0], list)
        assert len(result3[0]) == 3

    def test_insert_topic_tags(self, tagging_agent, query_agent, historian):
        try:
            now = format_timestamp(datetime.utcnow())
            headers = {headers_mod.DATE: now,
                       headers_mod.TIMESTAMP: now}
            to_send = [{'topic': 'devices/campus1/d1/all', 'headers': headers,
                        'message': [{'p1': 2, 'p2': 2}]}]
            query_agent.vip.rpc.call(historian, 'insert', to_send).get(
                timeout=10)
            gevent.sleep(2)

            query_agent.vip.rpc.call(
                tagging_agent,
                'add_topic_tags',
                topic_prefix='campus1/d1',
                tags={'campus': True, 'dis': "Test description"}).get(timeout=10)

            result3 = query_agent.vip.rpc.call(
                tagging_agent, 'get_tags_by_topic',
                topic_prefix='campus1/d1', include_kind=True,
                include_description=True, skip=0, count=3,
                order="LAST_TO_FIRST").get(timeout=10)

            # [['dis', 'Test description', 'Str', 'Short display name for an
            # entity.'],
            #  ['campus', '1', 'Marker',
            #   'Marks a campus that might have one or more site/building']]
            print(result3)
            assert len(result3) == 3
            assert len(result3[0]) == len(result3[1]) == 4
            assert result3[0][0] == 'id'
            assert result3[0][1] == 'campus1/d1'
            assert result3[0][2] == 'Ref'
            assert result3[0][3] == 'Unique identifier for an entity.'

            assert result3[1][0] == 'dis'
            assert result3[1][1] == 'Test description'
            assert result3[1][2] == 'Str'
            assert result3[1][3] == 'Short display name for an entity.'

            assert result3[2][0] == 'campus'
            assert result3[2][1]
            assert result3[2][2] == 'Marker'
            assert result3[2][
                       3] == 'Marks a campus that might have one or more ' \
                             'site/building'
        finally:
            self.cleanup(['topic_tags'])

    def test_topic_by_tags_custom_condition(self, tagging_agent, query_agent, historian):
        try:
            now = format_timestamp(datetime.utcnow())
            headers = {headers_mod.DATE: now,
                       headers_mod.TIMESTAMP: now}
            to_send = [{'topic': 'devices/campus1/d2/all', 'headers': headers,
                        'message': [
                            {'p1': 2, 'p2': 2, 'p3': 1, 'p4': 2, 'p5': 2}]}]
            query_agent.vip.rpc.call(historian, 'insert', to_send).get(
                timeout=10)
            to_send = [{'topic': 'devices/campus1/d1/all', 'headers': headers,
                        'message': [
                            {'p1': 2, 'p2': 2, 'p3': 1, 'p4': 2, 'p5': 2}]}]
            query_agent.vip.rpc.call(historian, 'insert', to_send).get(
                timeout=10)

            to_send = [{'topic': 'devices/campus2/d1/all', 'headers': headers,
                        'message': [
                            {'p1': 2, 'p2': 2, 'p3': 1, 'p4': 2, 'p5': 2}]}]
            query_agent.vip.rpc.call(historian, 'insert', to_send).get(
                timeout=10)
            gevent.sleep(2)

            # 2. Add tags to topics and topic_prefix that can be used for queries
            query_agent.vip.rpc.call(
                tagging_agent, 'add_topic_tags', topic_prefix='campus1',
                tags={'campus': True, 'dis': "Test description",
                      "geoCountry": "US"}).get(timeout=10)

            query_agent.vip.rpc.call(
                tagging_agent, 'add_topic_tags', topic_prefix='campus2',
                tags={'campus': True, "geoCountry": "UK"}).get(timeout=10)

            query_agent.vip.rpc.call(
                tagging_agent, 'add_tags',
                tags={
                    'campus.*/d.*/p1': {'point': True, 'maxVal': 15, 'minVal': -1},
                    'campus.*/d.*/p2': {'point': True, 'maxVal': 10, 'minVal': 0,
                                        'dis': "Test description"},
                    'campus.*/d.*/p3': {'point': True, 'maxVal': 5, 'minVal': 1,
                                        'dis': "Test description"},
                    'campus.*/d1': {'equip': True, 'elec': True, 'phase': 'p1_1',
                                    'dis': "Test description"},
                    'campus.*/d2': {'equip': True, 'elec': True,
                                    'phase': 'p2'},
                    'campus1/d.*': {'campusRef': 'campus1'},
                    'campus2/d.*': {'campusRef': 'campus2'}}).get(timeout=10)

            query_agent.vip.rpc.call(tagging_agent, 'add_topic_tags',
                                     topic_prefix='campus2/d1',
                                     tags={'phase': "p1_2"}).get(timeout=10)
            gevent.sleep(2)

            # 3. Query topic prefix by tags
            # Simple AND
            result1 = query_agent.vip.rpc.call(
                tagging_agent, 'get_topics_by_tags',
                condition="campus AND geoCountry='US'").get(timeout=10)
            print("Results of simple AND query: {} ".format(result1))
            assert len(result1) == 1
            assert result1[0] == 'campus1'

            # AND and OR precedence
            result1 = query_agent.vip.rpc.call(
                tagging_agent, 'get_topics_by_tags',
                condition='minVal<0 OR maxVal>=5 AND maxVal<10').get(timeout=10)
            print("Results of AND and OR query: {} ".format(result1))
            assert len(result1) == 6
            # Check  default order
            assert result1 == ['campus1/d1/p1', 'campus1/d1/p3', 'campus1/d2/p1',
                               'campus1/d2/p3', 'campus2/d1/p1', 'campus2/d1/p3']

            # Change precedence with parenthesis
            result1 = query_agent.vip.rpc.call(
                tagging_agent, 'get_topics_by_tags',
                condition='(minVal<0 OR maxVal>=5) AND maxVal<10').get(timeout=10)
            print("Results of AND and OR query with parenthesis: {} ".format(
                result1))
            assert len(result1) == 3
            assert result1 == ['campus1/d1/p3', 'campus1/d2/p3', 'campus2/d1/p3']

            # Verify skip, count and order
            result1 = query_agent.vip.rpc.call(
                tagging_agent, 'get_topics_by_tags',
                condition='(minVal<0 OR maxVal>=5) AND maxVal<10', skip=1,
                count=2, order="LAST_TO_FIRST").get(timeout=10)
            print("Results of query with skip and count: {}".format(result1))
            assert result1 == ['campus1/d2/p3', 'campus1/d1/p3']

            # Verify NOT
            result1 = query_agent.vip.rpc.call(
                tagging_agent, 'get_topics_by_tags',
                condition='NOT campus AND NOT point AND dis="Test '
                          'description"').get(timeout=10)
            print("Results of NOT query1: {}".format(result1))
            assert result1 == ['campus1/d1', 'campus2/d1']

            result1 = query_agent.vip.rpc.call(
                tagging_agent, 'get_topics_by_tags',
                condition='point AND NOT(maxVal>=5 AND minVal=1)').get(timeout=10)
            print("Results of NOT query2: {}".format(result1))
            assert result1 == ['campus1/d1/p1', 'campus1/d1/p2', 'campus1/d2/p1',
                               'campus1/d2/p2', 'campus2/d1/p1', 'campus2/d1/p2']

            # Verify unary minus
            result1 = query_agent.vip.rpc.call(
                tagging_agent, 'get_topics_by_tags',
                condition='minVal=-1').get(timeout=10)
            print("Results of unary minus query: {}".format(result1))
            assert result1 == ['campus1/d1/p1', 'campus1/d2/p1', 'campus2/d1/p1']

            # Verify LIKE
            result1 = query_agent.vip.rpc.call(
                tagging_agent,
                'get_topics_by_tags',
                condition='equip AND phase LIKE "p1.*"').get(timeout=10)
            print("Results of LIKE query: {}".format(result1))
            assert result1 == ['campus1/d1', 'campus2/d1']

            # NOT LIKE
            result1 = query_agent.vip.rpc.call(
                tagging_agent,
                'get_topics_by_tags',
                condition='equip AND NOT (phase LIKE "p1.*")').get(timeout=10)
            print("Result of NOT LIKE query: {}".format(result1))
            assert result1 == ['campus1/d2']

        finally:
            self.cleanup(['topic_tags'])

    def test_topic_by_tags_parent_topic_query(self, tagging_agent, query_agent, historian):
        try:
            now = format_timestamp(datetime.utcnow())
            headers = {headers_mod.DATE: now,
                       headers_mod.TIMESTAMP: now}
            to_send = [{'topic': 'devices/campus1/d2/all', 'headers': headers,
                        'message': [
                            {'p1': 2, 'p2': 2, 'p3': 1, 'p4': 2, 'p5': 2}]}]
            query_agent.vip.rpc.call(historian, 'insert', to_send).get(
                timeout=10)
            to_send = [{'topic': 'devices/campus1/d1/all', 'headers': headers,
                        'message': [
                            {'p1': 2, 'p2': 2, 'p3': 1, 'p4': 2, 'p5': 2}]}]
            query_agent.vip.rpc.call(historian, 'insert', to_send).get(
                timeout=10)

            to_send = [{'topic': 'devices/campus2/d1/all', 'headers': headers,
                        'message': [
                            {'p1': 2, 'p2': 2, 'p3': 1, 'p4': 2, 'p5': 2}]}]
            query_agent.vip.rpc.call(historian, 'insert', to_send).get(
                timeout=10)
            gevent.sleep(2)

            # 2. Add tags to topics and topic_prefix that can be used for queries
            query_agent.vip.rpc.call(
                tagging_agent, 'add_topic_tags', topic_prefix='campus1',
                tags={'campus': True, 'dis': "Test description",
                      "geoCountry": "US"}).get(timeout=10)

            query_agent.vip.rpc.call(
                tagging_agent, 'add_topic_tags', topic_prefix='campus2',
                tags={'campus': True, "geoCountry": "UK",
                      'dis': "United Kingdom"}).get(timeout=10)

            query_agent.vip.rpc.call(
                tagging_agent, 'add_tags',
                tags={
                    'campus.*/d.*/p1': {'point': True, 'maxVal': 15, 'minVal': -1},
                    'campus.*/d.*/p2': {'point': True, 'maxVal': 10, 'minVal': 0,
                                        'dis': "Test description"},
                    'campus.*/d.*/p3': {'point': True, 'maxVal': 5, 'minVal': 1,
                                        'dis': "Test description"},
                    'campus.*/d1': {'equip': True, 'elec': True, 'phase': 'p1_1',
                                    'dis': "Test description"},
                    'campus.*/d2': {'equip': True, 'elec': True,
                                    'phase': 'p2'},
                    'campus1/d.*': {'campusRef': 'campus1'},
                    'campus2/d.*': {'campusRef': 'campus2'}}).get(timeout=10)

            query_agent.vip.rpc.call(tagging_agent, 'add_topic_tags',
                                     topic_prefix='campus2/d1',
                                     tags={'phase': "p1_2"}).get(timeout=10)
            gevent.sleep(2)

            # 3. Query topic prefix by tags
            # Verify parent topic query
            result1 = query_agent.vip.rpc.call(
                tagging_agent,
                'get_topics_by_tags',
                condition='equip AND elec AND campusRef.geoCountry="UK"').get(
                timeout=10)
            print("Result of NOT LIKE query: {}".format(result1))
            assert result1 == ['campus2/d1']

            result1 = query_agent.vip.rpc.call(
                tagging_agent,
                'get_topics_by_tags',
                condition='equip AND elec AND campusRef.geoCountry LIKE "UK.*"'
            ).get(timeout=10)
            print("Result of NOT LIKE query: {}".format(result1))
            assert result1 == ['campus2/d1']

            result1 = query_agent.vip.rpc.call(
                tagging_agent,
                'get_topics_by_tags',
                condition='equip AND elec AND campusRef.geoCountry="UK" AND '
                          'campusRef.dis="United Kingdom"').get(timeout=10)
            print("Result of NOT LIKE query: {}".format(result1))
            assert result1 == ['campus2/d1']

            result1 = query_agent.vip.rpc.call(
                tagging_agent, 'get_topics_by_tags',
                condition='equip AND elec AND NOT(campusRef.geoCountry="UK" AND '
                          'campusRef.dis="United Kingdom")').get(timeout=10)
            print("Result of NOT LIKE query: {}".format(result1))
            assert result1 == ['campus1/d1', 'campus1/d2']

        finally:
            self.cleanup(['topic_tags'])

    def test_topic_by_tags_condition_errors(self, tagging_agent, query_agent):
        # Invalid tag name
        try:
            query_agent.vip.rpc.call(
                tagging_agent, 'get_topics_by_tags',
                condition='minValue<0 OR maxVal>=5').get(timeout=10)
            pytest.fail("Expected value error. Got none")
        except RemoteError as e:
            assert e.message == 'Invalid tag minValue at line number 1 and ' \
                                'column number 0'
            print(e.exc_info['exc_type'])

        # Missing parenthesis
        try:
            query_agent.vip.rpc.call(
                tagging_agent, 'get_topics_by_tags',
                condition='(equip OR ahu AND maxVal<10').get(timeout=10)
            pytest.fail("Expected value error. Got none")
        except RemoteError as e:
            pass

        # Invalid type after LIKE
        try:
            query_agent.vip.rpc.call(tagging_agent, 'get_topics_by_tags',
                                     condition='maxVal like 10').get(timeout=10)
            pytest.fail("Expected value error. Got none")
        except RemoteError as e:
            assert e.message == 'Syntax error in query condition. ' \
                                'Invalid token 10 at line ' \
                                'number 1 and column number 12'
