from requests import get, post
from datetime import datetime
from time import localtime, strftime
from base64 import b64encode
from hmac import new as h_new
from abc import ABCMeta
from json import dumps

from setting import link_v5_time, access_key, access_secret_key, access_pass_phrase, web_site
from .util import mode_json


class Rest(metaclass=ABCMeta):
    def __init__(self):
        self.str_timestamp = ''
        self.body = None
        self.request_path = None
        self.access_sign = ''
        self.header = ''
        self.mode = {}
        self.parameters = None

    @staticmethod
    def get_abs_path(link):
        return '{web_site}{link}'.format(web_site=web_site, link=link)

    def get_timestamp(self):
        return get(self.get_abs_path(link=link_v5_time)).json()['data'][0]['ts']

    def generate_access_timestamp(self):
        """
        函数名称:generate_access_timestamp
        函数功能:从官网获取时间戳或从本地获取时间戳
        输入参数:无
        """
        # noinspection PyBroadException
        try:
            sys_timestamp = self.get_timestamp()
            # get(self.get_abs_path(link=link_v5_time)).json()['data'][0]['ts']
            # 时差八小时
            local_diff = 0
            self.str_timestamp = strftime("%Y-%m-%dT%H:%M:%S.{sec}Z", localtime((int(sys_timestamp)-local_diff)/1000.0))
            self.str_timestamp = self.str_timestamp.format(sec=sys_timestamp[-3:])
        except:
            system_timestamp = datetime.utcnow()
            tmp_timestamp = system_timestamp.strftime('%Y-%m-%dT%H:%M:%S.')
            str_mic_sec = system_timestamp.strftime('%f')
            self.str_timestamp = tmp_timestamp + str_mic_sec[0:3] + 'Z'

    def generate_request_path(self):
        """
        函数名称:generate_request_path
        函数功能:通过parameters 生成路径
        输入参数:无
        """
        if self.parameters is not None:
            sub_path =  '&'.join([f'{key}={value}' for key, value in self.parameters.items()])
            self.request_path = ''.join((self.mode.get('request_link'), '?', sub_path))
        else:
            self.request_path = self.mode.get('request_link')

    def generate_access_sign(self):
        """
        函数名称:generate_access_sign
        函数功能:通过时间戳和method+path+body 生成数字签名
        输入参数:无
        """
        self.generate_access_timestamp()
        self.generate_request_path()

        if self.body is None:
            message = ''.join((
                str(self.str_timestamp),
                str.upper(self.mode['mode_method']),
                self.request_path
            ))
        else:
            message = ''.join((
                str(self.str_timestamp),
                str.upper(self.mode['mode_method']),
                self.mode['request_link'],
                str(self.body)
            ))
        mac = h_new(
            bytes(access_secret_key, encoding='utf-8'),
            bytes(message, encoding='utf-8'),
            digestmod='sha256'
        )
        self.access_sign = b64encode(mac.digest())

    def generate_header(self):
        if bool(self.mode.get('mode_header')) is True:
            self.generate_access_sign()
            self.header = {
                'Content-Type': 'application/json',
                'OK-ACCESS-KEY': access_key,
                'OK-ACCESS-SIGN': self.access_sign,
                'OK-ACCESS-TIMESTAMP': self.str_timestamp,
                'OK-ACCESS-PASSPHRASE': access_pass_phrase
            }
        else:
            self.header = None

    def generate_body(self):
        self.body = dumps(self.parameters) if bool(self.mode.get('mode_body')) else None

    def set_request(self, mode_name):
        self.mode = mode_json[mode_name]
        self.generate_body()
        self.generate_header()

    def http_get_data(self):
        get_data = get(
            url=self.get_abs_path(link=self.mode['request_link']),
            headers=self.header if self.mode['mode_header'] else None,
            params=self.parameters,
            timeout=30,
            allow_redirects=True
        )
        return get_data.json()

    def http_post_data(self):
        post_data = post(
            url=self.get_abs_path(link=self.mode['request_link']),
            data=self.body if self.mode['mode_body'] else None,
            headers=self.header if self.mode['mode_header'] else None
        )
        return post_data.json()

    def get_request_data(self, sub_mode, parameters=None):
        """
        函数名称:get_request_data
        函数功能:生成路径后。返回http数据,返回的数据格式由需求决定,数据格式并不统一
        输入参数:sub_mode mode名字
                :parameters 参数
        """
        if parameters:
            self.parameters = {k: str(v) for k, v in parameters.items()}
        else:
            self.parameters = None
        self.set_request(mode_name=sub_mode)

        request_data = {}
        if self.mode['mode_method'] == 'GET':
            request_data = self.http_get_data()
        elif self.mode['mode_method'] == 'POST':
            request_data = self.http_post_data()
        return request_data.get('data') if request_data.get('code') == '0' else request_data


# 资金
class RestAsset(Rest):
    def __init__(self):
        super().__init__()

    def get_asset_currencies(self):
        """
        函数名称:get_asset_currencies
        函数功能:获取平台所有币种列表。并非所有币种都可被用于交易
        输入参数:无
        """
        my_mode = 'asset_currencies'
        return super().get_request_data(sub_mode=my_mode)

    def get_asset_balances(self, **kwargs):
        """
        函数名称:get_asset_balances
        函数功能:获取资金账户所有资产列表,查询各币种的余额、冻结和可用等信息
        输入参数:ccy 币种 如BTC
        """
        my_mode = 'asset_balances'
        return super().get_request_data(sub_mode=my_mode, parameters=kwargs)

    def get_asset_bills(self, **kwargs):
        """
        函数名称:get_asset_bills
        函数功能:查询资金账户账单流水,可查询最近一个月的数据。
        输入参数:ccy 币种
        """
        my_mode = 'asset_bills'
        return super().get_request_data(sub_mode=my_mode, parameters=kwargs)

    def get_asset_deposit_address(self, **kwargs):
        """
        函数名称:get_asset_deposit_address
        函数功能:获取各个币种的充值地址,包括曾使用过的老地址。
                 IOTA充值地址不能重复使用!在向IOTA地址发起充值后,再次充值到此相同地址将不会被确认到账。
        输入参数:ccy 币种
        """
        my_mode = 'asset_deposit_address'
        return super().get_request_data(sub_mode=my_mode, parameters=kwargs)

    def get_asset_deposit_history(self, **kwargs):
        """
        函数名称:get_asset_deposit_history
        函数功能:根据币种,充值状态,时间范围获取充值记录,按照时间倒序排列,默认返回 100 条数据。
        输入参数:ccy 币种
        """
        my_mode = 'asset_deposit_history'
        return super().get_request_data(sub_mode=my_mode, parameters=kwargs)

    def get_asset_withdrawal_history(self, **kwargs):
        """
        函数名称:get_asset_withdrawal_history
        函数功能:根据币种,提币状态,时间范围获取提币记录,按照时间倒序排列,默认返回 100 条数据。
        输入参数:ccy 币种
        """
        my_mode = 'asset_withdrawal_history'
        return super().get_request_data(sub_mode=my_mode, parameters=kwargs)


class RestOrder(Rest):
    """
    类名称:RestOrder
    类说明:获取所有与订单有关系的功能,此功能需要登录。包括交易,最近的交易明细
    """
    def __init__(self):
        super().__init__()

    def order(self, **kwargs):
        """
        函数名称:order
        函数功能:下单
        输入参数:instId     是	产品ID,如 BTC-USD-190927-5000-C
                tdMode      是	交易模式
                    保证金模式:isolated:逐仓 ;cross:全仓
                    非保证金模式:cash:非保证金
                ccy         否	保证金币种,仅适用于单币种保证金模式下的全仓杠杆订单
                clOrdId     否	客户自定义订单ID 字母(区分大小写)与数字的组合,可以是纯字母、纯数字且长度要在1-32位之间。
                tag         否	订单标签 字母(区分大小写)与数字的组合,可以是纯字母、纯数字,且长度在1-8位之间。
                side        是	订单方向 buy:买 sell:卖
                posSide     可选	持仓方向 在双向持仓模式下必填,且仅可选择 long 或 short
                ordType     是	订单类型
                    market:市价单
                    limit:限价单
                    post_only:只做maker单
                    fok:全部成交或立即取消
                    ioc:立即成交并取消剩余
                    optimal_limit_ioc:市价委托立即成交并取消剩余(仅适用交割、永续)
                sz      是	委托数量
                px      可选	委托价格,仅适用于限价单
                reduceOnly  否	是否只减仓,true 或 false,默认false 仅适用于币币杠杆订单
        """
        my_mode = 'trade_order'
        return super().get_request_data(sub_mode=my_mode, parameters=kwargs)

    def get_order_information(self, **kwargs):
        """
        函数名称:get_order_information
        函数功能:查订单信息
        输入参数: instId
            ordId
        """
        my_mode = 'trade_order_information'
        return super().get_request_data(sub_mode=my_mode, parameters=kwargs)

    def get_trade_fills(self, **kwargs):
        """
        函数名称:get_trade_fills
        函数功能:获取近3天的订单成交明细信息
        输入参数:instType
            SPOT:币币
            MARGIN:币币杠杆
            SWAP:永续合约
            FUTURES:交割合约
            OPTION:期权
        """
        my_mode = 'trade_fills'
        return super().get_request_data(sub_mode=my_mode, parameters=kwargs)

    def get_trade_fills_history(self, **kwargs):
        """
            函数名称:get_trade_fills_history
            函数功能:获取近3个月订单成交明细信息
            输入参数:instType
                SPOT:币币
                MARGIN:币币杠杆
                SWAP:永续合约
                FUTURES:交割合约
                OPTION:期权
        """
        my_mode = 'trade_fills_history'
        return super().get_request_data(sub_mode=my_mode, parameters=kwargs)

    def get_orders_history(self, **kwargs):
        """
            函数名称:get_orders_history
            函数功能:获取最近7天的已经完结状态的订单数据,已经撤销的未成交单 只保留2小时
            输入参数:instType
                SPOT:币币
                MARGIN:币币杠杆
                SWAP:永续合约
                FUTURES:交割合约
                OPTION:期权
        """
        my_mode = 'trade_orders_history'
        return super().get_request_data(sub_mode=my_mode, parameters=kwargs)

    def get_orders_history_archive(self, **kwargs):
        """
            函数名称:get_orders_history_archive
            函数功能:获取最近3个月的已经完结状态的订单数据,已经撤销的未成交单 只保留2小时
            输入参数:instType
                SPOT:币币
                MARGIN:币币杠杆
                SWAP:永续合约
                FUTURES:交割合约
                OPTION:期权
        """
        my_mode = 'trade_orders_history_archive'
        return super().get_request_data(sub_mode=my_mode, parameters=kwargs)

class RestAccount(Rest):
    """
    类名称:RestAccount
    类说明:账户功能模块下的API接口。需要身份验证
    """
    def __init__(self):
        super().__init__()

    def get_account_balance(self, **kwargs):
        """
            函数名称:get_account_balance
            函数功能:获取账户中资金余额信息。免息额度和折算率都是公共数据,不在账户接口内展示
            输入参数:ccy 币种 支持多币种查询(不超过20个),币种之间半角逗号分隔
        """
        my_mode = 'account_balance'
        balance = super().get_request_data(sub_mode=my_mode, parameters=kwargs)
        return balance[0]['details']

    def get_account_positions(self, **kwargs):
        """
            函数名称:get_account_positions
            函数功能:获取该账户下拥有实际持仓的信息。账户为单向持仓模式会显示净持仓(net)
                    账户为双向持仓模式下会分别返回多头(long)或空头(short)的仓位。
            输入参数:instType
                MARGIN:币币杠杆
                SWAP:永续合约
                FUTURES:交割合约
                OPTION:期权
            说   明:instType和instId同时传入的时候会校验instId与instType是否一致,
                    结果返回instId的持仓信息
        """
        my_mode = 'account_positions'
        return super().get_request_data(sub_mode=my_mode, parameters=kwargs)

    def get_account_position_risk(self, **kwargs):
        """
            函数名称:get_account_position_risk
            函数功能:查看账户持仓风险
            输入参数:instType
                MARGIN:币币杠杆
                SWAP:永续合约
                FUTURES:交割合约
                OPTION:期权
        """
        my_mode = 'account_position_risk'
        return super().get_request_data(sub_mode=my_mode, parameters=kwargs)

    def get_account_bills(self, **kwargs):
        """
            函数名称:get_account_bills
            函数功能:账单流水查询(近七天)帐户资产流水是指导致帐户余额增加或减少的行为。
                     本接口可以查询最近7天的账单数据。
            输入参数:instType
                SPOT:币币
                MARGIN:币币杠杆
                SWAP:永续合约
                FUTURES:交割合约
                OPTION:期权
        """
        my_mode = 'account_bills'
        return super().get_request_data(sub_mode=my_mode, parameters=kwargs)

    def get_account_bills_archive(self, **kwargs):
        """
            函数名称:get_account_bills_archive
            函数功能:账单流水查询(近三月)帐户资产流水是指导致帐户余额增加或减少的行为
                     本接口可以查询最近3个月的账单数据。
            输入参数:instType
                SPOT:币币
                MARGIN:币币杠杆
                SWAP:永续合约
                FUTURES:交割合约
                OPTION:期权
        """
        my_mode = 'account_bills_archive'
        return super().get_request_data(sub_mode=my_mode, parameters=kwargs)

    def get_account_config(self, **kwargs):
        """
            函数名称:get_account_config
            函数功能:查看当前账户的配置信息。
        """
        my_mode = 'account_config'
        return super().get_request_data(sub_mode=my_mode, parameters=kwargs)


# 行情数据
class RestMarket(Rest):
    def __init__(self):
        super().__init__()

    def get_market_tickers(self, **kwargs):
        """
        函数名称:get_market_tickers
        函数功能:获取产品行情信息
        输入参数:inst_type
            SPOT:币币
            SWAP:永续合约
            FUTURES:交割合约
            OPTION:期权
        返回参数:
        """
        my_mode = 'market_tickers'
        return super().get_request_data(sub_mode=my_mode, parameters=kwargs)

    def get_market_ticker(self, **kwargs):
        """
        函数名称:get_market_ticker
        函数功能:获取单个产品行情信息
        输入参数:instId 产品ID
        返回参数:
        """
        my_mode = 'market_ticker'
        return super().get_request_data(sub_mode=my_mode, parameters=kwargs)

    def get_market_index_tickers(self, **kwargs):
        """
        函数名称:get_market_index_tickers
        函数功能:获取指数行情数据
        输入参数:quoteCcy 指数计价单位,
                目前只有 USD/USDT/BTC为计价单位的指数,
                quoteCcy和instId必须填写一个
                instId 指数,如 BTC-USD
        返回参数:
        """
        my_mode = 'market_index_tickers'
        return super().get_request_data(sub_mode=my_mode, parameters=kwargs)

    def get_market_books(self, **kwargs):
        """
        函数名称:get_market_books
        函数功能:获取产品深度列表
        输入参数:instId 产品ID
                 sz 档位深度数量
        返回参数:
        """
        my_mode = 'market_books'
        return super().get_request_data(sub_mode=my_mode, parameters=kwargs)

    def get_market_candles(self, **kwargs):
        """
        函数名称:get_market_candles
        函数功能:获取K线数据。K线数据按请求的粒度分组返回,K线数据每个粒度最多可获取最近1440条
        输入参数:instId: 产品ID
                 after: 请求此时间戳之前(更旧的数据)的分页内容,传的值为对应接口的ts
                 before: 请求此时间戳之后(更新的数据)的分页内容,传的值为对应接口的ts
                 bar: 时间粒度,默认值1m 如 [1m/3m/5m/15m/30m/1H/2H/4H/6H/12H/1D/1W/1M/3M/6M/1Y]
                 limit: 分页返回的结果集数量,最大为100,不填默认返回100条
        返回参数:
        """
        my_mode = 'market_candles'
        return super().get_request_data(sub_mode=my_mode, parameters=kwargs)

    def get_market_history_candles(self, **kwargs):
        """
        函数名称:get_market_history_candles
        函数功能:获取交易产品历史K线数据(仅主流币)
                OKB-USDT、BTC-USDT、ETH-USDT、LTC-USDT、ETC-USDT、XRP-USDT、EOS-USDT、BCH-USDT、BSV-USDT、TRX-USDT
        输入参数:instId: 产品ID
                 after: 请求此时间戳之前(更旧的数据)的分页内容,传的值为对应接口的ts
                 before: 请求此时间戳之后(更新的数据)的分页内容,传的值为对应接口的ts
                 bar: 时间粒度,默认值1m 如 [1m/3m/5m/15m/30m/1H/2H/4H/6H/12H/1D/1W/1M/3M/6M/1Y]
                 limit: 分页返回的结果集数量,最大为100,不填默认返回100条
        返回参数:
        """
        my_mode = 'market_history_candles'
        return super().get_request_data(sub_mode=my_mode, parameters=kwargs)

    def get_market_index_candles(self, **kwargs):
        """
        函数名称:get_market_index_candles
        函数功能:指数K线数据每个粒度最多可获取最近1440条。
        输入参数:instId: 现货指数
                 after: 请求此时间戳之前(更旧的数据)的分页内容,传的值为对应接口的ts
                 before: 请求此时间戳之后(更新的数据)的分页内容,传的值为对应接口的ts
                 bar: 时间粒度,默认值1m 如 [1m/3m/5m/15m/30m/1H/2H/4H/6H/12H/1D/1W/1M/3M/6M/1Y]
                 limit: 分页返回的结果集数量,最大为100,不填默认返回100条
        输出参数:
        """
        my_mode = 'market_index_candles'
        return super().get_request_data(sub_mode=my_mode, parameters=kwargs)

    def get_market_mark_price_candles(self, **kwargs):
        """
        函数名称:get_market_mark_price_candles
        函数功能:标记价格K线数据每个粒度最多可获取最近1440条。
        输入参数:instId: 现货指数
                 after: 请求此时间戳之前(更旧的数据)的分页内容,传的值为对应接口的ts
                 before: 请求此时间戳之后(更新的数据)的分页内容,传的值为对应接口的ts
                 bar: 时间粒度,默认值1m 如 [1m/3m/5m/15m/30m/1H/2H/4H/6H/12H/1D/1W/1M/3M/6M/1Y]
                 limit: 分页返回的结果集数量,最大为100,不填默认返回100条
        输出参数:
        """
        my_mode = 'market_mark_price_candles'
        return super().get_request_data(sub_mode=my_mode, parameters=kwargs)

    def get_market_trades(self, **kwargs):
        """
        函数名称:get_market_trades
        函数功能:查询市场上的成交信息数据。
        输入参数:inst_id: 产品ID
        输出参数:
        """
        my_mode = 'market_trades'
        return super().get_request_data(sub_mode=my_mode, parameters=kwargs)

    def get_index_candles(self, **kwargs):
        """
        函数名称:get_index_candles
        函数功能:获取指数K线数据
        输入参数:instId: 产品ID
            after: 请求此时间戳之前的分布内容，传的值为对应接口的ts
            before: 请求此时间戳之后的分布内容，传的值为对应接口的ts，单独使用时，会返回最新的数据
            bar: 时间粒度, 默认值1m
            limit: 分页返回的结果集数量，默认100
        输出参数:
        """
        my_mode = 'index_candles'
        return super().get_request_data(sub_mode=my_mode, parameters=kwargs)

    def get_history_index_candles(self, **kwargs):
        """
        函数名称:get_index_candles
        函数功能:获取指数K线数据
        输入参数:instId: 产品ID
            after: 请求此时间戳之前的分布内容，传的值为对应接口的ts
            before: 请求此时间戳之后的分布内容，传的值为对应接口的ts，单独使用时，会返回最新的数据
            bar: 时间粒度, 默认值1m
            limit: 分页返回的结果集数量，默认100
        输出参数:
        """
        my_mode = 'history_index_candles'
        return super().get_request_data(sub_mode=my_mode, parameters=kwargs)

# 公共数据
class RestPublic(Rest):
    def __init__(self):
        super().__init__()

    def get_public_instruments(self, **kwargs):
        """
        函数名称:get_public_instruments
        函数功能:获取所有可交易产品的信息列表。
        输入参数:inst_type [SPOT|SWAP|FUTURES|OPTION]
        返回参数:
        """
        my_mode = 'public_instruments'
        return super().get_request_data(sub_mode=my_mode, parameters=kwargs)
